/**
 * WebSocket Client Examples for Invisible Art Gallery
 * 
 * This file demonstrates how to connect to the WebSocket endpoints
 * for real-time updates in the Invisible Art Gallery application.
 */

/**
 * Connect to an artwork's WebSocket to receive updates when it's revealed
 * 
 * @param {string} artworkId - The ID of the artwork to monitor
 * @returns {WebSocket} The WebSocket connection
 */
function connectToArtworkSocket(artworkId) {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  const wsEndpoint = `${wsProtocol}//${host}/ws/artwork/${artworkId}/`;
  
  console.log(`Connecting to artwork socket: ${wsEndpoint}`);
  const socket = new WebSocket(wsEndpoint);
  
  socket.onopen = function(e) {
    console.log('Artwork socket connection established');
  };
  
  socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Artwork socket message received:', data);
    
    // Handle different message types
    switch (data.type) {
      case 'artwork_status':
        handleArtworkStatus(data);
        break;
      case 'artwork_revealed':
        handleArtworkRevealed(data);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };
  
  socket.onclose = function(e) {
    console.log('Artwork socket connection closed', e);
  };
  
  socket.onerror = function(e) {
    console.error('Artwork socket error:', e);
  };
  
  return socket;
}

/**
 * Connect to the notifications WebSocket to receive user notifications
 * 
 * @param {string} authToken - JWT authentication token
 * @returns {WebSocket} The WebSocket connection
 */
function connectToNotificationsSocket(authToken) {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  const wsEndpoint = `${wsProtocol}//${host}/ws/notifications/?token=${authToken}`;
  
  console.log('Connecting to notifications socket');
  const socket = new WebSocket(wsEndpoint);
  
  socket.onopen = function(e) {
    console.log('Notifications socket connection established');
  };
  
  socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Notification received:', data);
    
    // Handle different notification types
    switch (data.type) {
      case 'welcome':
        console.log('Connected to notification service');
        break;
      case 'notification':
        displayNotification(data.message, data.data);
        break;
      default:
        console.log('Unknown notification type:', data.type);
    }
  };
  
  socket.onclose = function(e) {
    console.log('Notifications socket connection closed', e);
  };
  
  socket.onerror = function(e) {
    console.error('Notifications socket error:', e);
  };
  
  return socket;
}

/**
 * Handle artwork status messages
 * 
 * @param {Object} data - Artwork status data
 */
function handleArtworkStatus(data) {
  console.log(`Artwork status: ${data.is_revealed ? 'Revealed' : 'Hidden'}`);
  
  // Example: Update UI based on artwork status
  if (data.is_revealed) {
    // Show the artwork if it's revealed
    document.getElementById('artwork-container').classList.remove('hidden');
    document.getElementById('artwork-title').textContent = data.artwork.title;
    // Load the artwork content (e.g., image)
    loadArtworkContent(data.artwork.id);
  } else {
    // Show countdown or conditions for unrevealed artwork
    document.getElementById('artwork-container').classList.add('hidden');
    document.getElementById('artwork-status').textContent = 'This artwork has not been revealed yet';
  }
}

/**
 * Handle artwork revealed messages
 * 
 * @param {Object} data - Artwork revealed data
 */
function handleArtworkRevealed(data) {
  console.log('Artwork has been revealed:', data.artwork);
  
  // Example: Show a celebration animation and load the artwork
  showRevealCelebration();
  
  // Update UI to show the revealed artwork
  document.getElementById('artwork-container').classList.remove('hidden');
  document.getElementById('artwork-title').textContent = data.artwork.title;
  document.getElementById('artwork-artist').textContent = `By ${data.artwork.artist}`;
  
  // Load the artwork content (e.g., image)
  loadArtworkContent(data.artwork.id);
}

/**
 * Display a notification to the user
 * 
 * @param {string} message - The notification message
 * @param {Object} data - Additional notification data
 */
function displayNotification(message, data) {
  console.log('Displaying notification:', message, data);
  
  // Example: Show a toast notification
  const notificationElement = document.createElement('div');
  notificationElement.className = 'toast-notification';
  notificationElement.textContent = message;
  
  document.body.appendChild(notificationElement);
  
  // Auto-remove the notification after 5 seconds
  setTimeout(() => {
    notificationElement.classList.add('fade-out');
    setTimeout(() => {
      document.body.removeChild(notificationElement);
    }, 500);
  }, 5000);
  
  // Handle specific notification types
  if (data && data.type === 'artwork_revealed') {
    // Example: Offer to navigate to the revealed artwork
    offerToNavigateToArtwork(data.artwork_id);
  }
}

/**
 * Example usage:
 * 
 * // Connect to an artwork's WebSocket
 * const artworkSocket = connectToArtworkSocket('some-artwork-id');
 * 
 * // Connect to the notifications WebSocket
 * const jwtToken = 'your-jwt-token';
 * const notificationsSocket = connectToNotificationsSocket(jwtToken);
 * 
 * // Disconnect from WebSockets when leaving the page
 * window.addEventListener('beforeunload', () => {
 *   artworkSocket.close();
 *   notificationsSocket.close();
 * });
 */ 