/**
 * CaptureScreen - Camera & GPS Capture
 * Takes geotagged photos for carbon credit evidence
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  View,
  TouchableOpacity,
  Text,
  Alert,
  SafeAreaView,
  ActivityIndicator,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as Location from 'expo-location';

const CaptureScreen = ({ navigation }) => {
  const cameraRef = useRef();
  const [permission, requestPermission] = useCameraPermissions();
  const [locationPermission, requestLocationPermission] = Location.useForegroundPermissions();
  const [location, setLocation] = useState(null);
  const [facing, setFacing] = useState('back');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    requestPermissions();
  }, []);

  const requestPermissions = async () => {
    // Camera permission
    if (!permission?.granted) {
      await requestPermission();
    }

    // Location permission
    if (!locationPermission?.granted) {
      await requestLocationPermission();
    }

    // Get current location
    getCurrentLocation();
  };

  const getCurrentLocation = async () => {
    try {
      const result = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });
      setLocation(result.coords);
    } catch (error) {
      Alert.alert('Error', 'Failed to get location: ' + error.message);
    }
  };

  const handleCapture = async () => {
    if (!cameraRef.current) return;

    try {
      setIsLoading(true);

      if (!location) {
        Alert.alert('Error', 'Unable to get GPS coordinates. Please try again.');
        return;
      }

      // Capture photo
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        base64: true,
      });

      // Navigate to submit screen with photo and location
      navigation.navigate('Submit', {
        photo: photo.uri,
        base64: photo.base64,
        latitude: location.latitude,
        longitude: location.longitude,
        accuracy: location.accuracy,
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to capture photo: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!permission?.granted || !locationPermission?.granted) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.permissionContainer}>
          <Text style={styles.permissionText}>
            This app needs camera and location permissions
          </Text>
          <TouchableOpacity
            style={styles.permissionButton}
            onPress={requestPermissions}
          >
            <Text style={styles.permissionButtonText}>Grant Permissions</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <CameraView style={styles.camera} facing={facing} ref={cameraRef}>
        <View style={styles.topBar}>
          <Text style={styles.locationText}>
            {location
              ? `📍 Lat: ${location.latitude.toFixed(4)}, Lng: ${location.longitude.toFixed(4)}`
              : 'Getting location...'}
          </Text>
        </View>

        <View style={styles.bottomControls}>
          <TouchableOpacity
            style={styles.flipButton}
            onPress={() => setFacing(facing === 'back' ? 'front' : 'back')}
          >
            <Text style={styles.flipButtonText}>🔄 Flip</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.captureButton, isLoading && styles.disabledButton]}
            onPress={handleCapture}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.captureButtonText}>📸 Capture</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.refreshButton}
            onPress={getCurrentLocation}
          >
            <Text style={styles.refreshButtonText}>🔄 Refresh Location</Text>
          </TouchableOpacity>
        </View>
      </CameraView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
    justifyContent: 'space-between',
  },
  topBar: {
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 12,
    marginTop: 10,
  },
  locationText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '600',
    textAlign: 'center',
  },
  bottomControls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingBottom: 30,
    backgroundColor: 'rgba(0,0,0,0.7)',
  },
  captureButton: {
    backgroundColor: '#1e5128',
    borderRadius: 50,
    padding: 20,
    width: 80,
    height: 80,
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButtonText: {
    color: '#fff',
    fontSize: 28,
  },
  flipButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 8,
  },
  flipButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  refreshButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 8,
  },
  refreshButtonText: {
    color: '#fff',
    fontSize: 12,
  },
  disabledButton: {
    opacity: 0.6,
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  permissionText: {
    fontSize: 16,
    marginBottom: 20,
    textAlign: 'center',
  },
  permissionButton: {
    backgroundColor: '#1e5128',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 8,
  },
  permissionButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
});

export default CaptureScreen;
