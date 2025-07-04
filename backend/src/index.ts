import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { bearerAuth } from 'hono/bearer-auth'
import * as bcrypt from 'bcryptjs'
import jwt from '@tsndr/cloudflare-worker-jwt'

// Define the environment interface
interface Env {
  DB: D1Database
  GALLERY_BUCKET: R2Bucket
  JWT_SECRET: string
  CLOUDFLARE_ACCOUNT_ID?: string
  CLOUDFLARE_API_TOKEN?: string
}

// Define context variables
interface Variables {
  jwtPayload: {
    userId: number
    username: string
    isAdmin: boolean
    exp: number
  }
}

// Create a new Hono app
const app = new Hono<{ Bindings: Env; Variables: Variables }>()

// Add CORS middleware
app.use('*', cors({
  origin: '*', // In production, replace with your app's domain
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization'],
}))

// Root endpoint
app.get('/', (c) => {
  return c.json({ 
    message: 'Design Gallery API', 
    version: '1.0.0',
    endpoints: {
      auth: ['/api/register', '/api/login'],
      designs: ['/api/designs', '/api/designs/:id', '/api/designs/featured', '/api/designs/categories'],
      admin: ['/api/admin/users', '/api/admin/approve-user', '/api/admin/designs', '/api/admin/upload-url'],
      settings: ['/api/settings', '/api/admin/settings'],
      favorites: ['/api/favorites', '/api/favorites/:id'],
      categories: ['/api/categories'],
      analytics: ['/api/designs/:id/view']
    },
    storage: 'Cloudflare R2',
    database: 'Cloudflare D1'
  })
})

// Health check endpoint
app.get('/health', (c) => {
  return c.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// Helper functions
const hashPassword = async (password: string): Promise<string> => {
  return await bcrypt.hash(password, 10)
}

const comparePassword = async (password: string, hash: string): Promise<boolean> => {
  return await bcrypt.compare(password, hash)
}

const signToken = async (payload: any, secret: string): Promise<string> => {
  return await jwt.sign(payload, secret)
}

const verifyToken = async (token: string, secret: string): Promise<any> => {
  return await jwt.verify(token, secret)
}

// Generate R2 object key for uploads
const generateR2Key = (filename: string, category: string = 'general'): string => {
  const timestamp = Date.now()
  const randomId = Math.random().toString(36).substring(2, 15)
  const cleanFilename = filename.replace(/[^a-zA-Z0-9.-]/g, '_')
  return `${category}/${timestamp}_${randomId}_${cleanFilename}`
}

// Generate public URL for R2 objects
const generatePublicUrl = (objectKey: string, accountId?: string): string => {
  if (accountId) {
    return `https://pub-${accountId}.r2.dev/${objectKey}`
  }
  return `https://design-gallery-images.your-domain.com/${objectKey}` // Update with your custom domain
}

// Authentication middleware
const authMiddleware = async (c: any, next: any) => {
  const authHeader = c.req.header('Authorization')
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return c.json({ error: 'Missing or invalid token' }, 401)
  }

  const token = authHeader.substring(7)
  try {
    const result = await verifyToken(token, c.env.JWT_SECRET)
    if (!result) {
      return c.json({ error: 'Invalid token' }, 401)
    }
    
    // Extract the actual payload from the nested structure
    const payload = result.payload || result
    c.set('jwtPayload', payload)
    await next()
  } catch (error) {
    return c.json({ error: 'Invalid token' }, 401)
  }
}

// Admin authentication middleware
const adminAuthMiddleware = async (c: any, next: any) => {
  const authHeader = c.req.header('Authorization')
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return c.json({ error: 'Missing or invalid token' }, 401)
  }

  const token = authHeader.substring(7)
  try {
    const result = await verifyToken(token, c.env.JWT_SECRET)
    if (!result) {
      return c.json({ error: 'Invalid token' }, 401)
    }
    
    // Extract the actual payload from the nested structure
    const payload = result.payload || result
    
    if (!payload.isAdmin) {
      return c.json({ error: 'Admin access required' }, 403)
    }
    
    c.set('jwtPayload', payload)
    await next()
  } catch (error) {
    return c.json({ error: 'Invalid token' }, 401)
  }
}

// Authentication routes
app.post('/api/register', async (c) => {
  try {
    const { username, password } = await c.req.json()
    
    if (!username || !password) {
      return c.json({ error: 'Username and password are required' }, 400)
    }

    if (password.length < 6) {
      return c.json({ error: 'Password must be at least 6 characters long' }, 400)
    }

    // Check if user already exists
    const existingUser = await c.env.DB.prepare(
      'SELECT id FROM users WHERE username = ?'
    ).bind(username).first()

    if (existingUser) {
      return c.json({ error: 'Username already taken' }, 409)
    }

    // Hash password and create user
    const hashedPassword = await hashPassword(password)
    
    await c.env.DB.prepare(
      'INSERT INTO users (username, password_hash, is_admin, is_approved) VALUES (?, ?, 0, 1)'
    ).bind(username, hashedPassword).run()

    return c.json({ 
      message: 'User registered successfully and approved.' 
    }, 201)

  } catch (error) {
    console.error('Registration error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.post('/api/login', async (c) => {
  try {
    const { username, password } = await c.req.json()
    
    if (!username || !password) {
      return c.json({ error: 'Username and password are required' }, 400)
    }

    // Get user from database
    const user = await c.env.DB.prepare(
      'SELECT id, username, password_hash, is_admin, is_approved FROM users WHERE username = ?'
    ).bind(username).first()

    if (!user) {
      return c.json({ error: 'Invalid credentials' }, 401)
    }

    // Verify password
    const isValidPassword = await comparePassword(password, user.password_hash as string)
    if (!isValidPassword) {
      return c.json({ error: 'Invalid credentials' }, 401)
    }

    // Check if user is approved
    if (!user.is_approved) {
      return c.json({ error: 'User not approved. Please wait for admin approval.' }, 401)
    }

    // Create JWT token
    const tokenPayload = {
      userId: user.id,
      username: user.username,
      isAdmin: !!user.is_admin,
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hours
    }

    const token = await signToken(tokenPayload, c.env.JWT_SECRET)

    return c.json({ 
      token,
      user: {
        id: user.id,
        username: user.username,
        isAdmin: !!user.is_admin
      }
    })

  } catch (error) {
    console.error('Login error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

// Design endpoints
app.get('/api/designs', authMiddleware, async (c) => {
  try {
    const page = parseInt(c.req.query('page') || '1')
    const limit = parseInt(c.req.query('limit') || '20')
    const category = c.req.query('category')
    const style = c.req.query('style')
    const colour = c.req.query('colour')
    const fabric = c.req.query('fabric')
    const occasion = c.req.query('occasion')
    const featured = c.req.query('featured')
    const search = c.req.query('search')
    const offset = (page - 1) * limit

    let sql = 'SELECT * FROM designs WHERE status = "active"'
    const params: any[] = []

    if (category) {
      sql += ' AND category = ?'
      params.push(category)
    }

    if (style) {
      sql += ' AND style = ?'
      params.push(style)
    }

    if (colour) {
      sql += ' AND colour = ?'
      params.push(colour)
    }

    if (fabric) {
      sql += ' AND fabric = ?'
      params.push(fabric)
    }

    if (occasion) {
      sql += ' AND occasion = ?'
      params.push(occasion)
    }

    if (featured === 'true') {
      sql += ' AND featured = 1'
    }

    if (search) {
      sql += ' AND (title LIKE ? OR description LIKE ? OR short_description LIKE ? OR tags LIKE ? OR designer_name LIKE ? OR collection_name LIKE ?)'
      const searchPattern = `%${search}%`
      params.push(searchPattern, searchPattern, searchPattern, searchPattern, searchPattern, searchPattern)
    }

    sql += ' ORDER BY featured DESC, created_at DESC LIMIT ? OFFSET ?'
    params.push(limit, offset)

    const designs = await c.env.DB.prepare(sql).bind(...params).all()

    // Get total count for pagination
    let countSql = 'SELECT COUNT(*) as total FROM designs WHERE status = "active"'
    const countParams: any[] = []

    if (category) {
      countSql += ' AND category = ?'
      countParams.push(category)
    }

    if (style) {
      countSql += ' AND style = ?'
      countParams.push(style)
    }

    if (colour) {
      countSql += ' AND colour = ?'
      countParams.push(colour)
    }

    if (fabric) {
      countSql += ' AND fabric = ?'
      countParams.push(fabric)
    }

    if (occasion) {
      countSql += ' AND occasion = ?'
      countParams.push(occasion)
    }

    if (featured === 'true') {
      countSql += ' AND featured = 1'
    }

    if (search) {
      countSql += ' AND (title LIKE ? OR description LIKE ? OR short_description LIKE ? OR tags LIKE ? OR designer_name LIKE ? OR collection_name LIKE ?)'
      const searchPattern = `%${search}%`
      countParams.push(searchPattern, searchPattern, searchPattern, searchPattern, searchPattern, searchPattern)
    }

    const countResult = await c.env.DB.prepare(countSql).bind(...countParams).first()

    return c.json({
      designs: designs.results,
      totalCount: countResult?.total || 0,
      page,
      limit,
      totalPages: Math.ceil(Number(countResult?.total || 0) / limit)
    })

  } catch (error) {
    console.error('Get designs error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.get('/api/designs/featured', authMiddleware, async (c) => {
  try {
    const limit = parseInt(c.req.query('limit') || '10')
    
    const designs = await c.env.DB.prepare(
      'SELECT * FROM designs WHERE status = "active" AND featured = 1 ORDER BY created_at DESC LIMIT ?'
    ).bind(limit).all()

    return c.json({ designs: designs.results })

  } catch (error) {
    console.error('Get featured designs error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.get('/api/designs/:id', authMiddleware, async (c) => {
  try {
    const id = c.req.param('id')
    
    const design = await c.env.DB.prepare(
      'SELECT * FROM designs WHERE id = ? AND status = "active"'
    ).bind(id).first()

    if (!design) {
      return c.json({ error: 'Design not found' }, 404)
    }

    return c.json({ design })

  } catch (error) {
    console.error('Get design error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.post('/api/designs/:id/view', authMiddleware, async (c) => {
  try {
    const id = c.req.param('id')
    const payload = c.get('jwtPayload')
    const userAgent = c.req.header('User-Agent') || ''
    
    // Record the view
    await c.env.DB.prepare(
      'INSERT INTO design_views (design_id, user_id, ip_address) VALUES (?, ?, ?)'
    ).bind(id, payload.userId, userAgent.substring(0, 255)).run()

    // Update view count
    await c.env.DB.prepare(
      'UPDATE designs SET view_count = view_count + 1 WHERE id = ?'
    ).bind(id).run()

    return c.json({ message: 'View recorded' })

  } catch (error) {
    console.error('Record view error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.post('/api/designs', adminAuthMiddleware, async (c) => {
  try {
    const { 
      title, 
      description, 
      short_description,
      long_description,
      r2_object_key,
      category, 
      style,
      colour,
      fabric,
      occasion,
      size_available,
      price_range,
      tags, 
      featured,
      designer_name,
      collection_name,
      season
    } = await c.req.json()
    
    if (!title || !r2_object_key || !category) {
      return c.json({ error: 'Title, R2 object key, and category are required' }, 400)
    }

    // Generate public URL from R2 object key
    const image_url = generatePublicUrl(r2_object_key, c.env.CLOUDFLARE_ACCOUNT_ID)

    const result = await c.env.DB.prepare(
      `INSERT INTO designs (
        title, description, short_description, long_description, image_url, r2_object_key,
        category, style, colour, fabric, occasion, size_available, price_range, tags, 
        featured, designer_name, collection_name, season, created_by
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      title, 
      description || '', 
      short_description || '',
      long_description || description || '',
      image_url,
      r2_object_key,
      category, 
      style || '',
      colour || '',
      fabric || '',
      occasion || '',
      size_available || '',
      price_range || '',
      tags || '', 
      featured ? 1 : 0,
      designer_name || '',
      collection_name || '',
      season || '',
      c.get('jwtPayload').userId
    ).run()

    if (!result.success) {
      return c.json({ error: 'Failed to create design' }, 500)
    }

    // Get the created design
    const design = await c.env.DB.prepare(
      'SELECT * FROM designs WHERE id = ?'
    ).bind(result.meta.last_row_id).first()

    return c.json({ design, message: 'Design created successfully' }, 201)

  } catch (error) {
    console.error('Create design error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.put('/api/designs/:id', adminAuthMiddleware, async (c) => {
  try {
    const id = c.req.param('id')
    const updateData = await c.req.json()
    
    // Build dynamic update query
    const allowedFields = [
      'title', 'description', 'short_description', 'long_description', 'category', 
      'style', 'colour', 'fabric', 'occasion', 'size_available', 'price_range', 
      'tags', 'featured', 'status', 'designer_name', 'collection_name', 'season'
    ]
    
    const updates = []
    const params = []
    
    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates.push(`${key} = ?`)
        params.push(value)
      }
    }
    
    if (updates.length === 0) {
      return c.json({ error: 'No valid fields to update' }, 400)
    }
    
    // Add updated_at
    updates.push('updated_at = CURRENT_TIMESTAMP')
    params.push(id)
    
    const sql = `UPDATE designs SET ${updates.join(', ')} WHERE id = ?`
    
    const result = await c.env.DB.prepare(sql).bind(...params).run()
    
    if (!result.success) {
      return c.json({ error: 'Failed to update design' }, 500)
    }
    
    if (result.meta.changes === 0) {
      return c.json({ error: 'Design not found' }, 404)
    }
    
    // Get the updated design
    const design = await c.env.DB.prepare(
      'SELECT * FROM designs WHERE id = ?'
    ).bind(id).first()
    
    return c.json({ design, message: 'Design updated successfully' })
    
  } catch (error) {
    console.error('Update design error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.delete('/api/designs/:id', adminAuthMiddleware, async (c) => {
  try {
    const id = c.req.param('id')
    
    // Get design info for R2 cleanup
    const design = await c.env.DB.prepare(
      'SELECT r2_object_key FROM designs WHERE id = ?'
    ).bind(id).first()
    
    if (!design) {
      return c.json({ error: 'Design not found' }, 404)
    }
    
    // Delete from R2
    try {
      await c.env.GALLERY_BUCKET.delete(design.r2_object_key as string)
    } catch (r2Error) {
      console.error('R2 deletion error:', r2Error)
      // Continue with database deletion even if R2 fails
    }
    
    // Delete from database
    const result = await c.env.DB.prepare(
      'DELETE FROM designs WHERE id = ?'
    ).bind(id).run()

    if (!result.success) {
      return c.json({ error: 'Failed to delete design' }, 500)
    }

    return c.json({ message: 'Design deleted successfully' })

  } catch (error) {
    console.error('Delete design error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

// Admin upload URL generation for R2
app.post('/api/admin/upload-url', adminAuthMiddleware, async (c) => {
  try {
    const { filename, category = 'general', contentType } = await c.req.json()
    
    if (!filename) {
      return c.json({ error: 'Filename is required' }, 400)
    }
    
    // Generate R2 object key
    const objectKey = generateR2Key(filename, category)
    
    // For direct upload to R2, we'll use a different approach
    // Generate a presigned POST URL using R2's httpMetadata
    const options: R2PutOptions = {
      httpMetadata: {
        contentType: contentType || 'application/octet-stream'
      }
    }
    
    // Since R2 doesn't have built-in presigned URLs like S3, we'll return the object key
    // and let the client upload directly using the Worker as a proxy
    const uploadUrl = `/api/admin/upload/${encodeURIComponent(objectKey)}`
    
    // Generate public URL
    const publicUrl = generatePublicUrl(objectKey, c.env.CLOUDFLARE_ACCOUNT_ID)
    
    return c.json({
      uploadUrl,
      objectKey,
      publicUrl,
      expiresIn: 3600
    })

  } catch (error) {
    console.error('Upload URL generation error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

// Categories management
app.get('/api/categories', authMiddleware, async (c) => {
  try {
    const categories = await c.env.DB.prepare(
      'SELECT * FROM categories WHERE is_active = 1 ORDER BY sort_order ASC, name ASC'
    ).all()

    return c.json({ categories: categories.results })
  } catch (error) {
    console.error('Get categories error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

// Favorites management
app.get('/api/favorites', authMiddleware, async (c) => {
  try {
    const payload = c.get('jwtPayload')
    
    const favorites = await c.env.DB.prepare(
      `SELECT d.* FROM designs d 
       JOIN user_favorites uf ON d.id = uf.design_id 
       WHERE uf.user_id = ? AND d.status = "active"
       ORDER BY uf.created_at DESC`
    ).bind(payload.userId).all()

    return c.json({ favorites: favorites.results })
  } catch (error) {
    console.error('Get favorites error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.post('/api/favorites/:id', authMiddleware, async (c) => {
  try {
    const designId = c.req.param('id')
    const payload = c.get('jwtPayload')
    
    // Check if design exists
    const design = await c.env.DB.prepare(
      'SELECT id FROM designs WHERE id = ? AND status = "active"'
    ).bind(designId).first()
    
    if (!design) {
      return c.json({ error: 'Design not found' }, 404)
    }
    
    // Add to favorites (will ignore if already exists due to UNIQUE constraint)
    try {
      await c.env.DB.prepare(
        'INSERT INTO user_favorites (user_id, design_id) VALUES (?, ?)'
      ).bind(payload.userId, designId).run()
      
      return c.json({ message: 'Added to favorites' })
    } catch (error) {
      // Already exists
      return c.json({ message: 'Already in favorites' })
    }

  } catch (error) {
    console.error('Add favorite error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.delete('/api/favorites/:id', authMiddleware, async (c) => {
  try {
    const designId = c.req.param('id')
    const payload = c.get('jwtPayload')
    
    await c.env.DB.prepare(
      'DELETE FROM user_favorites WHERE user_id = ? AND design_id = ?'
    ).bind(payload.userId, designId).run()

    return c.json({ message: 'Removed from favorites' })

  } catch (error) {
    console.error('Remove favorite error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

// Admin user management
app.get('/api/admin/users', adminAuthMiddleware, async (c) => {
  try {
    const users = await c.env.DB.prepare(
      'SELECT id, username, is_admin, is_approved, created_at FROM users ORDER BY created_at DESC'
    ).all()

    return c.json({ users: users.results })
  } catch (error) {
    console.error('Get users error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.post('/api/admin/approve-user', adminAuthMiddleware, async (c) => {
  try {
    const { userId, approved } = await c.req.json()
    
    if (typeof userId !== 'number' || typeof approved !== 'boolean') {
      return c.json({ error: 'Invalid request data' }, 400)
    }

    const result = await c.env.DB.prepare(
      'UPDATE users SET is_approved = ? WHERE id = ?'
    ).bind(approved ? 1 : 0, userId).run()

    if (!result.success) {
      return c.json({ error: 'Failed to update user' }, 500)
    }

    return c.json({ message: 'User approval status updated successfully' })

  } catch (error) {
    console.error('Approve user error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

// App settings
app.get('/api/settings', async (c) => {
  try {
    const settings = await c.env.DB.prepare(
      'SELECT * FROM app_settings WHERE id = 1'
    ).first()

    return c.json(settings || { 
      allow_screenshots: 0, 
      allow_downloads: 0,
      watermark_enabled: 1,
      maintenance_mode: 0 
    })
  } catch (error) {
    console.error('Get settings error:', error)
    return c.json({ 
      allow_screenshots: 0, 
      allow_downloads: 0,
      watermark_enabled: 1,
      maintenance_mode: 0 
    })
  }
})

app.put('/api/admin/settings', adminAuthMiddleware, async (c) => {
  try {
    const updateData = await c.req.json()
    
    const allowedFields = [
      'allow_screenshots', 'allow_downloads', 'watermark_enabled', 'max_upload_size',
      'supported_formats', 'gallery_per_page', 'featured_designs_count', 'maintenance_mode',
      'app_version'
    ]
    
    const updates = []
    const params = []
    
    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates.push(`${key} = ?`)
        params.push(value)
      }
    }
    
    if (updates.length === 0) {
      return c.json({ error: 'No valid fields to update' }, 400)
    }
    
    updates.push('updated_at = CURRENT_TIMESTAMP')
    
    const sql = `UPDATE app_settings SET ${updates.join(', ')} WHERE id = 1`
    
    const result = await c.env.DB.prepare(sql).bind(...params).run()
    
    if (!result.success) {
      return c.json({ error: 'Failed to update settings' }, 500)
    }
    
    // Get updated settings
    const settings = await c.env.DB.prepare(
      'SELECT * FROM app_settings WHERE id = 1'
    ).first()
    
    return c.json({ settings, message: 'Settings updated successfully' })

  } catch (error) {
    console.error('Update settings error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

// Analytics endpoint
app.get('/api/admin/analytics', adminAuthMiddleware, async (c) => {
  try {
    const period = c.req.query('period') || '7' // days
    
    // Get basic stats
    const stats = await c.env.DB.batch([
      c.env.DB.prepare('SELECT COUNT(*) as total_designs FROM designs WHERE status = "active"'),
      c.env.DB.prepare('SELECT COUNT(*) as total_users FROM users WHERE is_approved = 1'),
      c.env.DB.prepare('SELECT COUNT(*) as total_views FROM design_views WHERE viewed_at > datetime("now", "-' + period + ' days")'),
      c.env.DB.prepare('SELECT COUNT(*) as featured_designs FROM designs WHERE featured = 1 AND status = "active"')
    ])
    
    // Get top viewed designs
    const topDesigns = await c.env.DB.prepare(
      'SELECT id, title, view_count FROM designs WHERE status = "active" ORDER BY view_count DESC LIMIT 10'
    ).all()
    
    // Get category distribution
    const categoryStats = await c.env.DB.prepare(
      'SELECT category, COUNT(*) as count FROM designs WHERE status = "active" GROUP BY category ORDER BY count DESC'
    ).all()
    
    return c.json({
      stats: {
        totalDesigns: (stats[0].results[0] as any)?.total_designs || 0,
        totalUsers: (stats[1].results[0] as any)?.total_users || 0,
        totalViews: (stats[2].results[0] as any)?.total_views || 0,
        featuredDesigns: (stats[3].results[0] as any)?.featured_designs || 0
      },
      topDesigns: topDesigns.results,
      categoryStats: categoryStats.results,
      period: parseInt(period)
    })

  } catch (error) {
    console.error('Get analytics error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

// Search endpoint
app.get('/api/search', authMiddleware, async (c) => {
  try {
    const query = c.req.query('q')
    const category = c.req.query('category')
    const limit = parseInt(c.req.query('limit') || '50')
    
    if (!query) {
      return c.json({ designs: [] })
    }

    let sql = `SELECT * FROM designs WHERE status = "active" AND (
      title LIKE ? OR description LIKE ? OR short_description LIKE ? OR 
      long_description LIKE ? OR tags LIKE ? OR designer_name LIKE ? OR 
      collection_name LIKE ? OR style LIKE ? OR colour LIKE ? OR fabric LIKE ?
    )`
    const searchPattern = `%${query}%`
    const params: any[] = Array(10).fill(searchPattern)

    if (category) {
      sql += ' AND category = ?'
      params.push(category)
    }

    sql += ' ORDER BY featured DESC, view_count DESC, created_at DESC LIMIT ?'
    params.push(limit)

    const designs = await c.env.DB.prepare(sql).bind(...params).all()

    return c.json({ designs: designs.results, query, category })

  } catch (error) {
    console.error('Search designs error:', error)
    return c.json({ error: 'Internal server error' }, 500)
  }
})

// 404 handler
app.notFound((c) => {
  return c.json({ error: 'Endpoint not found' }, 404)
})

// Error handler
app.onError((err, c) => {
  console.error('Unhandled error:', err)
  return c.json({ error: 'Internal server error' }, 500)
})

export default app 