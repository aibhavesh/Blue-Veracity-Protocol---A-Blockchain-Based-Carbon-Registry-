/**
 * StatusScreen - Submission Tracking
 * Displays verification status and minted NFT details
 */

import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  SafeAreaView,
  Image,
} from 'react-native';
import config from '../config';

const StatusScreen = ({ route, navigation }) => {
  const { submissionId } = route.params;
  const [submission, setSubmission] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    fetchStatus();
    // Poll for status updates every 5 seconds
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    if (isLoading) {
      setIsLoading(true);
    } else {
      setIsRefreshing(true);
    }

    try {
      const response = await fetch(
        `${config.apiBaseUrl}/submission/${submissionId}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch status');
      }

      const data = await response.json();
      setSubmission(data);
    } catch (error) {
      if (isLoading) {
        Alert.alert('Error', 'Failed to load submission: ' + error.message);
      }
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#1e5128" />
          <Text style={styles.loadingText}>Loading submission status...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!submission) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Submission not found</Text>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const getStatusColor = () => {
    switch (submission.status) {
      case 'PENDING':
        return '#ff9800';
      case 'VERIFIED':
        return '#4caf50';
      case 'FAILED':
        return '#f44336';
      default:
        return '#666';
    }
  };

  const getStatusIcon = () => {
    switch (submission.status) {
      case 'PENDING':
        return '⏳';
      case 'VERIFIED':
        return '✅';
      case 'FAILED':
        return '❌';
      default:
        return 'ℹ️';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.content}
        refreshing={isRefreshing}
        onRefresh={fetchStatus}
        showsVerticalScrollIndicator={false}
      >
        {/* Status Card */}
        <View
          style={[
            styles.statusCard,
            { borderLeftColor: getStatusColor() },
          ]}
        >
          <View style={styles.statusHeader}>
            <Text style={styles.statusIcon}>{getStatusIcon()}</Text>
            <View>
              <Text style={styles.statusLabel}>Status</Text>
              <Text style={[styles.statusValue, { color: getStatusColor() }]}>
                {submission.status}
              </Text>
            </View>
          </View>
        </View>

        {/* Submission ID */}
        <View style={styles.infoSection}>
          <Text style={styles.sectionTitle}>Submission Details</Text>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>ID:</Text>
            <Text style={styles.infoValue}>{submission.submission_id}</Text>
          </View>

          {/* Wallet Address */}
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Wallet:</Text>
            <Text style={styles.infoValue} numberOfLines={1}>
              {submission.wallet_address}
            </Text>
          </View>

          {/* Location */}
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Location:</Text>
            <Text style={styles.infoValue}>
              {submission.latitude.toFixed(6)}, {submission.longitude.toFixed(6)}
            </Text>
          </View>

          {/* Credits */}
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Credits:</Text>
            <Text style={styles.infoValue}>
              {submission.credits_amount} tCO2e
            </Text>
          </View>

          {/* Created Date */}
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Submitted:</Text>
            <Text style={styles.infoValue}>
              {new Date(submission.created_at).toLocaleString()}
            </Text>
          </View>
        </View>

        {/* IPFS Hash */}
        <View style={styles.infoSection}>
          <Text style={styles.sectionTitle}>Evidence</Text>
          <View style={styles.hashContainer}>
            <Text style={styles.hashLabel}>Evidence IPFS:</Text>
            <Text style={styles.hashValue} selectable>
              {submission.ipfs_hash}
            </Text>
            <Text style={styles.hashLink}>
              🔗 https://ipfs.io/ipfs/{submission.ipfs_hash}
            </Text>
          </View>
        </View>

        {/* Verified Details (if minted) */}
        {submission.status === 'VERIFIED' && (
          <View style={styles.verifiedSection}>
            <Text style={styles.sectionTitle}>🎖️  NFT Minted</Text>

            <View style={styles.infoItem}>
              <Text style={styles.infoLabel}>Token ID:</Text>
              <Text style={styles.infoValue}>{submission.token_id}</Text>
            </View>

            <View style={styles.hashContainer}>
              <Text style={styles.hashLabel}>Transaction Hash:</Text>
              <Text style={styles.hashValue} selectable>
                {submission.transaction_hash}
              </Text>
              <Text style={styles.hashLink}>
                🔗 https://amoy.polygonscan.com/tx/{submission.transaction_hash}
              </Text>
            </View>

            <View style={styles.hashContainer}>
              <Text style={styles.hashLabel}>Metadata URI:</Text>
              <Text style={styles.hashValue} selectable>
                {submission.metadata_hash}
              </Text>
            </View>

            <TouchableOpacity
              style={styles.viewNFTButton}
              onPress={() => {
                Alert.alert(
                  'View NFT',
                  `Token ID: ${submission.token_id}\n\nYour carbon credit NFT has been successfully minted on Polygon Amoy!`,
                  [{ text: 'OK' }]
                );
              }}
            >
              <Text style={styles.viewNFTButtonText}>👁️  View NFT Details</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Pending Message */}
        {submission.status === 'PENDING' && (
          <View style={styles.pendingSection}>
            <Text style={styles.pendingTitle}>⏳ Awaiting Verification</Text>
            <Text style={styles.pendingText}>
              A verifier will review your carbon credit evidence and mint the NFT.
              This typically takes 24-48 hours.
            </Text>
            <Text style={styles.refreshHint}>Pull down to refresh status</Text>
          </View>
        )}

        {/* Action Buttons */}
        <View style={styles.buttonGroup}>
          <TouchableOpacity
            style={styles.refreshButton}
            onPress={fetchStatus}
            disabled={isRefreshing}
          >
            <Text style={styles.refreshButtonText}>
              {isRefreshing ? '⏳ Refreshing...' : '🔄 Refresh Status'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.newSubmissionButton}
            onPress={() => navigation.popToTop()}
          >
            <Text style={styles.newSubmissionButtonText}>➕ New Submission</Text>
          </TouchableOpacity>
        </View>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
    color: '#f44336',
    marginBottom: 16,
  },
  statusCard: {
    backgroundColor: '#fff',
    borderLeftWidth: 4,
    borderRadius: 8,
    padding: 16,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  statusLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  statusValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  infoSection: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#1e5128',
    marginBottom: 12,
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoLabel: {
    fontSize: 13,
    color: '#666',
    fontWeight: '600',
  },
  infoValue: {
    fontSize: 13,
    color: '#333',
    fontWeight: '500',
    flex: 1,
    textAlign: 'right',
  },
  hashContainer: {
    backgroundColor: '#f9f9f9',
    borderRadius: 6,
    padding: 12,
    marginBottom: 12,
  },
  hashLabel: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
    marginBottom: 6,
  },
  hashValue: {
    fontSize: 11,
    color: '#333',
    fontFamily: 'monospace',
    backgroundColor: '#fff',
    borderRadius: 4,
    padding: 8,
    marginBottom: 6,
  },
  hashLink: {
    fontSize: 11,
    color: '#1e88e5',
    fontWeight: '500',
  },
  verifiedSection: {
    backgroundColor: '#e8f5e9',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#4caf50',
  },
  viewNFTButton: {
    backgroundColor: '#4caf50',
    borderRadius: 6,
    padding: 12,
    alignItems: 'center',
    marginTop: 12,
  },
  viewNFTButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
  pendingSection: {
    backgroundColor: '#fff3cd',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#ff9800',
  },
  pendingTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#ff6f00',
    marginBottom: 8,
  },
  pendingText: {
    fontSize: 13,
    color: '#666',
    lineHeight: 19,
    marginBottom: 8,
  },
  refreshHint: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
  buttonGroup: {
    gap: 10,
    marginBottom: 20,
  },
  refreshButton: {
    backgroundColor: '#1e5128',
    borderRadius: 8,
    padding: 14,
    alignItems: 'center',
  },
  refreshButtonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 15,
  },
  newSubmissionButton: {
    backgroundColor: '#1e88e5',
    borderRadius: 8,
    padding: 14,
    alignItems: 'center',
  },
  newSubmissionButtonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 15,
  },
  backButton: {
    backgroundColor: '#1e5128',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 6,
  },
  backButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
});

export default StatusScreen;
