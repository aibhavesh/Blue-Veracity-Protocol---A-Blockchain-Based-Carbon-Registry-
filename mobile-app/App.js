/**
 * Blue Veracity Protocol - React Native Mobile App
 * Field User Interface for Carbon Credit Submission
 */

import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View } from 'react-native';

import CaptureScreen from './screens/CaptureScreen';
import SubmitScreen from './screens/SubmitScreen';
import StatusScreen from './screens/StatusScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Initialize app
    async function prepare() {
      try {
        // Load fonts, images, etc.
        setIsReady(true);
      } catch (e) {
        // Initialization failed - set ready anyway to avoid blocking
        setIsReady(true);
      }
    }

    prepare();
  }, []);

  if (!isReady) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#0000ff" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#1e5128',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 18,
          },
        }}
      >
        <Stack.Screen
          name="Capture"
          component={CaptureScreen}
          options={{
            title: 'Blue Carbon Credit',
            headerShown: true,
          }}
        />
        <Stack.Screen
          name="Submit"
          component={SubmitScreen}
          options={{
            title: 'Submit Evidence',
          }}
        />
        <Stack.Screen
          name="Status"
          component={StatusScreen}
          options={{
            title: 'Verification Status',
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
