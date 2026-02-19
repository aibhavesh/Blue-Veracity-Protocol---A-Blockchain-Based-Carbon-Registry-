/**
 * SubmitScreen - Wallet Connection & Submission
 * Connects MetaMask and submits carbon credit evidence
 */

import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  Image,
  ScrollView,
  Alert,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { TextInput } from 'react-native-gesture-handler';
import config from '../config';

const SubmitScreen = ({ route, navigation }) => {
  const { photo, latitude, longitude, accuracy } = route.params;

  const [walletAddress, setWalletAddress] = useState('');
  const [creditsAmount, setCreditsAmount] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const connectMetaMask = async () => {
    setIsConnecting(true);
    try {
      // In production, use WalletConnect or similar for mobile
      // For now, we'll use a simplified approach
      Alert.alert(
        'MetaMask',
        'Please manually enter your wallet address or use WalletConnect bridge',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to connect wallet: ' + error.message);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleSubmit = async () => {
    // Validate inputs
    if (!walletAddress || !walletAddress.startsWith('0x') || walletAddress.length !== 42) {
      Alert.alert('Error', 'Please enter a valid Ethereum address (42 characters starting with 0x)');
      return;
    }

    if (!creditsAmount || parseFloat(creditsAmount) <= 0) {
      Alert.alert('Error', 'Please enter a valid credits amount');
      return;
    }

    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('file', {
        uri: photo,
        type: 'image/jpeg',
        name: `carbon-credit-${Date.now()}.jpg`,
      });
      formData.append('latitude', latitude);
      formData.append('longitude', longitude);
      formData.append('wallet_address', walletAddress);
      formData.append('credits_amount', parseFloat(creditsAmount));

      // Submit to backend using config
      const response = await fetch(`${config.apiBaseUrl}/submit`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Submission failed');
      }

      const result = await response.json();

      Alert.alert(
        'Success',
        `Submission ID: ${result.submission_id}\n\nYour carbon credit has been submitted for verification!`,
        [
          {
            text: 'View Status',
            onPress: () =>
              navigation.navigate('Status', {
                submissionId: result.submission_id,
              }),
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to submit: ' + error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Photo Preview */}
        <View style={styles.previewContainer}>
          <Image source={{ uri: photo }} style={styles.preview} />
          <Text style={styles.photoLabel}>Evidence Photo</Text>
        </View>

        {/* Location Info */}
        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>📍 Location</Text>
          <Text style={styles.infoText}>
            Latitude: {latitude.toFixed(6)}
          </Text>
          <Text style={styles.infoText}>
            Longitude: {longitude.toFixed(6)}
          </Text>
          <Text style={styles.infoText}>
            Accuracy: ±{accuracy.toFixed(1)}m
          </Text>
        </View>

        {/* Wallet Address */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Ethereum Wallet Address *</Text>
          <View style={styles.addressInputContainer}>
            <TextInput
              style={styles.input}
              placeholder="0x..."
              value={walletAddress}
              onChangeText={setWalletAddress}
              placeholderTextColor="#999"
              editable={!isConnecting}
            />
            <TouchableOpacity
              style={styles.connectButton}
              onPress={connectMetaMask}
              disabled={isConnecting}
            >
              {isConnecting ? (
                <ActivityIndicator color="#fff" size="small" />
              ) : (
                <Text style={styles.connectButtonText}>🦊 Connect</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>

        {/* Credits Amount */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Carbon Credits (tCO2e) *</Text>
          <TextInput
            style={styles.input}
            placeholder="2.5"
            value={creditsAmount}
            onChangeText={setCreditsAmount}
            placeholderTextColor="#999"
            keyboardType="decimal-pad"
            editable={!isSubmitting}
          />
          <Text style={styles.hint}>Metric tons of CO2 equivalent</Text>
        </View>

        {/* Info Box */}
        <View style={styles.warningBox}>
          <Text style={styles.warningTitle}>⚠️  Important</Text>
          <Text style={styles.warningText}>
            By submitting this evidence, you certify that the information is accurate and the
            carbon credit claim is legitimate. False submissions are fraud.
          </Text>
        </View>

        {/* Submit Button */}
        <TouchableOpacity
          style={[styles.submitButton, isSubmitting && styles.disabledButton]}
          onPress={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitButtonText}>🚀 Submit for Verification</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.cancelButton}
          onPress={() => navigation.goBack()}
          disabled={isSubmitting}
        >
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 16,
  },
  previewContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  preview: {
    width: '100%',
    height: 250,
    borderRadius: 8,
    marginBottom: 10,
  },
  photoLabel: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  infoBox: {
    backgroundColor: '#e8f5e9',
    borderLeftWidth: 4,
    borderLeftColor: '#1e5128',
    padding: 12,
    borderRadius: 4,
    marginBottom: 20,
  },
  infoTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#1e5128',
  },
  infoText: {
    fontSize: 13,
    color: '#333',
    marginBottom: 4,
  },
  formGroup: {
    marginBottom: 18,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 6,
    padding: 12,
    fontSize: 14,
    flex: 1,
  },
  addressInputContainer: {
    flexDirection: 'row',
    gap: 10,
  },
  connectButton: {
    backgroundColor: '#1e5128',
    borderRadius: 6,
    paddingHorizontal: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  connectButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 12,
  },
  hint: {
    fontSize: 12,
    color: '#999',
    marginTop: 6,
  },
  warningBox: {
    backgroundColor: '#fff3cd',
    borderLeftWidth: 4,
    borderLeftColor: '#ff9800',
    padding: 12,
    borderRadius: 4,
    marginBottom: 20,
  },
  warningTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#ff6f00',
    marginBottom: 6,
  },
  warningText: {
    fontSize: 12,
    color: '#666',
    lineHeight: 18,
  },
  submitButton: {
    backgroundColor: '#1e5128',
    borderRadius: 8,
    padding: 14,
    alignItems: 'center',
    marginBottom: 10,
  },
  submitButtonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
  cancelButton: {
    backgroundColor: '#eee',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginBottom: 20,
  },
  cancelButtonText: {
    color: '#666',
    fontWeight: '600',
    fontSize: 14,
  },
  disabledButton: {
    opacity: 0.6,
  },
});

export default SubmitScreen;
