import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import PlatformImage from '@/components/ui/PlatformImage';
import { Design } from '@/services/galleryApi';
import { router } from 'expo-router';

interface DesignCardProps {
  design: Design;
  onPress?: () => void;
}

const { width } = Dimensions.get('window');
const cardWidth = (width - 60) / 2; // 2 cards per row with margin

export default function DesignCard({ design, onPress }: DesignCardProps) {
  const handlePress = () => {
    if (onPress) {
      onPress();
    } else {
      // TODO: Navigate to design detail when screen is created
      console.log('Navigate to design:', design.id);
    }
  };

  return (
    <TouchableOpacity style={styles.container} onPress={handlePress}>
      <PlatformImage
        source={{ uri: design.image_url }}
        style={styles.image}
        resizeMode="cover"
      />
      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={2}>
          {design.title}
        </Text>
        <Text style={styles.category}>{design.category}</Text>
        {design.tags && (
          <Text style={styles.tags} numberOfLines={1}>
            {design.tags}
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    width: cardWidth,
    backgroundColor: 'white',
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  image: {
    width: '100%',
    height: 150,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  content: {
    padding: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  category: {
    fontSize: 12,
    color: '#666',
    textTransform: 'capitalize',
    marginBottom: 4,
  },
  tags: {
    fontSize: 11,
    color: '#999',
    fontStyle: 'italic',
  },
}); 