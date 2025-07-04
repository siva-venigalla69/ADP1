// Sample designs data for testing
const sampleDesigns = [
  {
    title: "Modern UI Dashboard",
    description: "A clean and modern dashboard design with beautiful charts and data visualization.",
    image_url: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop",
    category: "UI/UX",
    tags: "dashboard, modern, charts, data",
    created_by: 1
  },
  {
    title: "Mobile App Landing Page",
    description: "Responsive landing page design for mobile application showcase.",
    image_url: "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=300&fit=crop",
    category: "Web",
    tags: "landing page, mobile, responsive, app",
    created_by: 1
  },
  {
    title: "E-commerce Product Card",
    description: "Beautiful product card design for e-commerce applications.",
    image_url: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=300&fit=crop",
    category: "Mobile",
    tags: "ecommerce, product, card, shopping",
    created_by: 1
  },
  {
    title: "Brand Identity Package",
    description: "Complete brand identity design including logo, colors, and typography.",
    image_url: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300&fit=crop",
    category: "Branding",
    tags: "branding, logo, identity, colors",
    created_by: 1
  },
  {
    title: "Business Card Design",
    description: "Professional business card design with modern typography.",
    image_url: "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=400&h=300&fit=crop",
    category: "Print",
    tags: "business card, print, professional, typography",
    created_by: 1
  },
  {
    title: "Social Media Template",
    description: "Instagram post template with modern gradient design.",
    image_url: "https://images.unsplash.com/photo-1611262588024-d12430b98920?w=400&h=300&fit=crop",
    category: "Web",
    tags: "social media, instagram, template, gradient",
    created_by: 1
  },
  {
    title: "Portfolio Website",
    description: "Creative portfolio website design for designers and developers.",
    image_url: "https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=400&h=300&fit=crop",
    category: "Web",
    tags: "portfolio, website, creative, design",
    created_by: 1
  },
  {
    title: "Mobile Banking App",
    description: "Clean and secure mobile banking application interface design.",
    image_url: "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=400&h=300&fit=crop",
    category: "Mobile",
    tags: "banking, mobile, app, finance, security",
    created_by: 1
  },
  {
    title: "Food Delivery App UI",
    description: "Colorful and appetizing food delivery app interface design.",
    image_url: "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop",
    category: "UI/UX",
    tags: "food, delivery, app, colorful, restaurant",
    created_by: 1
  },
  {
    title: "Minimalist Poster",
    description: "Clean minimalist poster design for modern art gallery.",
    image_url: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop",
    category: "Print",
    tags: "poster, minimalist, art, gallery, clean",
    created_by: 1
  },
  {
    title: "Corporate Website Header",
    description: "Professional website header design for corporate businesses.",
    image_url: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop",
    category: "Web",
    tags: "corporate, website, header, professional, business",
    created_by: 1
  },
  {
    title: "Travel App Interface",
    description: "Beautiful travel app interface with stunning destination photos.",
    image_url: "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=400&h=300&fit=crop",
    category: "Mobile",
    tags: "travel, app, interface, destinations, photos",
    created_by: 1
  }
];

async function seedDesigns() {
  try {
    console.log('🌱 Starting to seed design data...');
    
    const API_URL = 'http://localhost:8787';
    
    console.log('🔑 Getting admin token...');
    
    // Login as admin to get token
    const loginResponse = await fetch(`${API_URL}/api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
      })
    });

    if (!loginResponse.ok) {
      const errorText = await loginResponse.text();
      throw new Error(`Failed to login as admin: ${errorText}`);
    }

    const { token } = await loginResponse.json();
    console.log('✅ Admin login successful');

    // Add each design
    let successCount = 0;
    let errorCount = 0;

    for (const design of sampleDesigns) {
      try {
        const response = await fetch(`${API_URL}/api/designs`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(design)
        });

        if (response.ok) {
          successCount++;
          const result = await response.json();
          console.log(`✅ Added design: ${design.title} (ID: ${result.design.id})`);
        } else {
          errorCount++;
          const error = await response.text();
          console.log(`❌ Failed to add design: ${design.title} - ${error}`);
        }
      } catch (error) {
        errorCount++;
        console.log(`❌ Error adding design: ${design.title} - ${error.message}`);
      }
    }

    console.log(`\n📊 Seeding completed:`);
    console.log(`✅ Successfully added: ${successCount} designs`);
    console.log(`❌ Failed to add: ${errorCount} designs`);
    console.log(`🎉 Gallery is ready for testing!`);

  } catch (error) {
    console.error('❌ Seeding failed:', error.message);
  }
}

// Just run it
seedDesigns(); 