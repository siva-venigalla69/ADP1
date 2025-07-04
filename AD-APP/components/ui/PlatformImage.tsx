import React from 'react';
import { ImageStyle, StyleProp } from 'react-native';
import { Image, ImageContentFit } from 'expo-image';

interface PlatformImageProps {
  source: { uri: string };
  style: StyleProp<ImageStyle>;
  resizeMode?: ImageContentFit;
}

export default function PlatformImage({ source, style, resizeMode = 'cover' }: PlatformImageProps) {
  // Use expo-image which works on all platforms
  return (
    <Image
      source={source}
      style={style}
      contentFit={resizeMode}
      transition={200}
    />
  );
} 