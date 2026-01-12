<template>
  <div class="map-page">
    <aside class="sidebar">
      <header class="sidebar-header">
        <h2 class="sidebar-title">Locations</h2>
        <button class="btn-text-danger" @click="clearAllMarkers" v-if="markers.length > 0">Clear all</button>
      </header>
      <div class="marker-list">
        <div v-if="markers.length === 0" class="empty-state">
          <span class="empty-icon">📍</span>
          <p>No locations yet</p>
          <span class="empty-hint">Click on the map to add one</span>
        </div>
        <div
          v-for="marker in markers"
          :key="marker.id"
          class="marker-item"
          @click="panToMarker(marker)"
        >
          <span class="marker-name">{{ marker.title }}</span>
          <button class="btn-icon" @click.stop="deleteMarker(marker.id)">×</button>
        </div>
      </div>
    </aside>

    <main class="map-main">
      <header class="map-header">
        <div class="header-left">
          <h1 class="map-title">Campus Map</h1>
        </div>
        <div class="header-actions">
          <button 
            class="btn-secondary"
            :class="{ active: routeMode }"
            @click="toggleRouteMode"
          >
            {{ routeMode ? 'Exit Route' : 'Find Path' }}
          </button>
          <button class="btn-secondary" @click="getCurrentLocation">
            My Location
          </button>
        </div>
      </header>
      
      <div v-if="routeMode" class="route-panel">
        <div class="route-status" :class="routeInfo.type">
          <span class="route-title">{{ routeInfo.title }}</span>
          <span class="route-desc">{{ routeInfo.description }}</span>
        </div>
        <div v-if="routeData" class="route-details">
          <div class="route-stat">
            <span class="stat-value">{{ (routeData.distance / 1000).toFixed(2) }}</span>
            <span class="stat-label">km</span>
          </div>
          <div class="route-stat">
            <span class="stat-value">{{ Math.round(routeData.duration / 60) }}</span>
            <span class="stat-label">min</span>
          </div>
          <button class="btn-text-danger" @click="clearRoute">Clear</button>
        </div>
      </div>

      <div class="map-wrapper">
        <l-map
          ref="map"
          :zoom="zoom"
          :center="center"
          @click="handleMapClick"
          class="leaflet-map"
        >
          <l-tile-layer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
          
          <l-polyline
            v-if="routePath"
            :lat-lngs="routePath"
            color="#5a6b7c"
            weight="4"
            opacity="0.8"
          />
          
          <l-marker
            v-if="routeStart"
            :lat-lng="routeStart"
            :icon="startIcon"
          >
            <l-popup>Start Point</l-popup>
          </l-marker>
          
          <l-marker
            v-if="routeEnd"
            :lat-lng="routeEnd"
            :icon="endIcon"
          >
            <l-popup>End Point</l-popup>
          </l-marker>
          
          <l-marker
            v-for="marker in markers"
            :key="marker.id"
            :lat-lng="[marker.latitude, marker.longitude]"
            :ref="el => setMarkerRef(el, marker.id)"
          >
            <l-popup>
              <div class="popup-content">
                <h4 class="popup-title">{{ marker.title }}</h4>
                <p class="popup-desc" v-if="marker.description">{{ marker.description }}</p>
                <div class="popup-actions">
                  <template v-if="routeMode">
                    <button class="popup-btn" @click="setAsRoutePoint(marker, 'start')">Set Start</button>
                    <button class="popup-btn" @click="setAsRoutePoint(marker, 'end')">Set End</button>
                  </template>
                  <button class="popup-btn danger" @click="deleteMarker(marker.id)">Delete</button>
                </div>
              </div>
            </l-popup>
          </l-marker>
          
          <l-marker
            v-if="currentLocation"
            :lat-lng="[currentLocation.lat, currentLocation.lng]"
          >
            <l-popup>
              <div class="popup-content">
                <h4 class="popup-title">Current Location</h4>
                <div class="popup-actions" v-if="routeMode">
                  <button class="popup-btn" @click="setAsRoutePoint({latitude: currentLocation.lat, longitude: currentLocation.lng}, 'start')">Set Start</button>
                  <button class="popup-btn" @click="setAsRoutePoint({latitude: currentLocation.lat, longitude: currentLocation.lng}, 'end')">Set End</button>
                </div>
              </div>
            </l-popup>
          </l-marker>
        </l-map>
      </div>
      
      <el-dialog v-model="dialogVisible" title="Add Location" width="360px" class="add-marker-dialog">
        <el-form :model="markerForm" label-position="top">
          <el-form-item label="Name">
            <el-input v-model="markerForm.title" placeholder="e.g., University Library"></el-input>
          </el-form-item>
          <el-form-item label="Description">
            <el-input
              v-model="markerForm.description"
              type="textarea"
              rows="3"
              placeholder="Optional description"
            ></el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <button class="btn-ghost" @click="dialogVisible = false">Cancel</button>
          <button class="btn-primary" @click="addMarker">Add</button>
        </template>
      </el-dialog>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { LMap, LTileLayer, LMarker, LPopup, LPolyline } from '@vue-leaflet/vue-leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet/dist/leaflet.js'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// Fix Leaflet default icon issue
import L from 'leaflet'
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
})

const map = ref(null)
const zoom = ref(13)
const center = ref([22.3193, 114.1694]) // Hong Kong coordinates
const markers = ref([])
const currentLocation = ref(null)
const dialogVisible = ref(false)
const markerForm = ref({
  title: '',
  description: '',
  latitude: 0,
  longitude: 0
})

const markerRefs = reactive({})

const setMarkerRef = (el, id) => {
  if (el) {
    markerRefs[id] = el
  }
}

// Routing related state
const routeMode = ref(false)
const routeStart = ref(null)
const routeEnd = ref(null)
const routePath = ref(null)
const routeData = ref(null)
const routeInfo = ref({
  title: 'Path Finding Mode',
  type: 'info',
  description: 'Click on markers or use "Set as Start/End" buttons to select route points'
})

// Custom icons
const startIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

const endIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

const loadMarkers = async () => {
  try {
    const response = await axios.get('/api/map/markers')
    markers.value = response.data.markers
  } catch (error) {
    ElMessage.error('Failed to load markers')
  }
}

const panToMarker = (marker) => {
  center.value = [marker.latitude, marker.longitude]
  zoom.value = 15
  // Open popup
  const markerRef = markerRefs[marker.id];
  if (markerRef && markerRef.leafletObject) {
    markerRef.leafletObject.openPopup();
  }
}

const deleteMarker = async (id) => {
  ElMessageBox.confirm(
    'Are you sure you want to delete this marker?',
    'Warning',
    {
      confirmButtonText: 'OK',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`/api/map/markers/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      markers.value = markers.value.filter(m => m.id !== id);
      ElMessage.success('Marker deleted successfully');
    } catch (error) {
      if (error.response?.status === 401) {
        ElMessage.error('Please login first');
      } else {
        ElMessage.error('Failed to delete marker');
      }
    }
  }).catch(() => {
    // Cancelled
  });
};

const clearAllMarkers = async () => {
  if(markers.value.length === 0) {
    ElMessage.info('There are no markers to clear.');
    return;
  }

  ElMessageBox.confirm(
    'Are you sure you want to delete all markers? This action cannot be undone.',
    'Warning',
    {
      confirmButtonText: 'Delete All',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const token = localStorage.getItem('token');
      // In a real app, you'd want a single API endpoint to do this efficiently.
      for (const marker of markers.value) {
        await axios.delete(`/api/map/markers/${marker.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      markers.value = [];
      ElMessage.success('All markers cleared successfully');
    } catch (error) {
      if (error.response?.status === 401) {
        ElMessage.error('Please login first');
      } else {
        ElMessage.error('Failed to clear all markers. Please try again.');
      }
    }
  }).catch(() => {
    // Cancelled
  });
};


const getCurrentLocation = () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        currentLocation.value = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        }
        center.value = [position.coords.latitude, position.coords.longitude]
        ElMessage.success('Current location obtained')
      },
      (error) => {
        ElMessage.error('Unable to get location information')
      }
    )
  } else {
    ElMessage.error('Your browser does not support geolocation.')
  }
}

const handleMapClick = (event) => {
  if (routeMode.value) {
    ElMessage.info('In route mode, you can only set start/end points using existing markers.');
    return;
  }
  markerForm.value.latitude = event.latlng.lat
  markerForm.value.longitude = event.latlng.lng
  dialogVisible.value = true
}

const addMarker = async () => {
  if (!markerForm.value.title) {
    ElMessage.warning('Please enter a title')
    return
  }
  
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post('/api/map/markers', markerForm.value, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    markers.value.push(response.data.marker)
    dialogVisible.value = false
    markerForm.value = { title: '', description: '', latitude: 0, longitude: 0 }
    ElMessage.success('Marker added successfully')
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.error('Please login first')
    } else {
      ElMessage.error('Failed to add marker')
    }
  }
}

// Routing related functions
const toggleRouteMode = () => {
  routeMode.value = !routeMode.value
  if (!routeMode.value) {
    clearRoute()
  } else {
    routeInfo.value = {
      title: 'Path Finding Mode',
      type: 'info',
      description: 'Use the buttons on markers or your current location to set route points.'
    }
  }
}

const setAsRoutePoint = (marker, type) => {
  if (type === 'start') {
    routeStart.value = [marker.latitude, marker.longitude]
    routeInfo.value = {
      title: 'Start Point Set',
      type: 'success',
      description: 'Start point selected. Now select an end point.'
    }
  } else if (type === 'end') {
    routeEnd.value = [marker.latitude, marker.longitude]
    routeInfo.value = {
      title: 'End Point Set',
      type: 'success',
      description: 'End point selected. Calculating route...'
    }
    calculateRoute()
  }
}

const calculateRoute = async () => {
  if (!routeStart.value || !routeEnd.value) {
    ElMessage.warning('Please select both start and end points')
    return
  }

  try {
    const response = await axios.post('/api/map/route', {
      start: routeStart.value,
      end: routeEnd.value
    })

    if (response.data.route) {
      // Convert coordinate format from [longitude, latitude] to [latitude, longitude]
      routePath.value = response.data.route.coordinates.map(coord => [coord[1], coord[0]])
      routeData.value = response.data.route
      
      routeInfo.value = {
        title: 'Route Calculated Successfully',
        type: 'success',
        description: `Route found: ${(response.data.route.distance / 1000).toFixed(2)} km, ${Math.round(response.data.route.duration / 60)} minutes`
      }
      
      // Adjust map view to show the entire path
      if (map.value && map.value.leafletObject) {
        const bounds = L.latLngBounds([routeStart.value, routeEnd.value])
        map.value.leafletObject.fitBounds(bounds, { padding: [50, 50] })
      }
    }
  } catch (error) {
    console.error('Route calculation error:', error)
    routeInfo.value = {
      title: 'Route Calculation Failed',
      type: 'error',
      description: error.response?.data?.error || 'Failed to calculate route. Please try again.'
    }
    ElMessage.error('Failed to calculate route')
  }
}

const clearRoute = () => {
  routeStart.value = null
  routeEnd.value = null
  routePath.value = null
  routeData.value = null
  routeInfo.value = {
    title: 'Path Finding Mode',
    type: 'info',
    description: 'Use the buttons on markers or your current location to set route points.'
  }
}

onMounted(() => {
  loadMarkers()
})
</script>

<style scoped>
.map-page {
  display: flex;
  height: calc(100vh - 120px);
  margin: calc(-1 * var(--spacing-lg));
}

.sidebar {
  width: 280px;
  flex-shrink: 0;
  background: var(--color-bg-elevated);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.sidebar-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.btn-text-danger {
  background: none;
  border: none;
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.btn-text-danger:hover {
  opacity: 0.7;
}

.marker-list {
  flex: 1;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl) var(--spacing-lg);
  color: var(--color-text-muted);
}

.empty-icon {
  font-size: 32px;
  margin-bottom: var(--spacing-sm);
  opacity: 0.5;
}

.empty-state p {
  margin: 0 0 var(--spacing-xs);
  font-size: var(--font-size-sm);
}

.empty-hint {
  font-size: var(--font-size-xs);
}

.marker-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.marker-item:hover {
  background: var(--color-bg-subtle);
}

.marker-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.btn-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-size: 18px;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.btn-icon:hover {
  background: var(--color-bg-muted);
  color: var(--color-danger);
}

.map-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.map-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-elevated);
  border-bottom: 1px solid var(--color-border-light);
}

.map-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-secondary {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary:hover {
  border-color: var(--color-border-focus);
  color: var(--color-text-primary);
}

.btn-secondary.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.route-panel {
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-subtle);
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-lg);
}

.route-status {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.route-status.success .route-title {
  color: var(--color-success);
}

.route-status.error .route-title {
  color: var(--color-danger);
}

.route-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.route-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.route-details {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.route-stat {
  text-align: center;
}

.stat-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin-left: 2px;
}

.map-wrapper {
  flex: 1;
  position: relative;
}

.leaflet-map {
  height: 100%;
  width: 100%;
}

/* Popup styles */
.popup-content {
  min-width: 150px;
}

.popup-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--spacing-xs);
  color: var(--color-text-primary);
}

.popup-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-sm);
}

.popup-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.popup-btn {
  padding: 4px 8px;
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 11px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.popup-btn:hover {
  border-color: var(--color-border-focus);
  color: var(--color-text-primary);
}

.popup-btn.danger:hover {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

/* Dialog styles */
.add-marker-dialog .btn-ghost,
.add-marker-dialog .btn-primary {
  margin-left: var(--spacing-sm);
}

.btn-ghost {
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-ghost:hover {
  border-color: var(--color-border-focus);
  color: var(--color-text-primary);
}

.btn-primary {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  color: #fff;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}
</style>
