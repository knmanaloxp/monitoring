import { useState, useEffect } from 'react'
import { Container, Grid, Paper, Typography, Box } from '@mui/material'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'
import DeviceList from './components/DeviceList'
import DeviceFilters from './components/DeviceFilters'
import NetworkQualityCard from './components/NetworkQualityCard'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

function App() {
  const [devices, setDevices] = useState([])
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [metrics, setMetrics] = useState([])
  const [filters, setFilters] = useState({
    location: '',
    user: '',
    ssid: '',
  })

  useEffect(() => {
    fetchDevices()
    const interval = setInterval(fetchDevices, 30000) // Refresh every 30 seconds
    
    // Add event listener for device refresh
    const handleRefresh = () => fetchDevices()
    window.addEventListener('refreshDevices', handleRefresh)
    
    return () => {
      clearInterval(interval)
      window.removeEventListener('refreshDevices', handleRefresh)
    }
  }, [])

  useEffect(() => {
    if (selectedDevice) {
      fetchDeviceMetrics(selectedDevice.id)
    }
  }, [selectedDevice])

  const fetchDevices = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/devices')
      const data = await response.json()
      setDevices(data)
    } catch (error) {
      console.error('Error fetching devices:', error)
    }
  }

  const fetchDeviceMetrics = async (deviceId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/devices/${deviceId}/metrics?timeframe=hour`)
      const data = await response.json()
      setMetrics(data)
    } catch (error) {
      console.error('Error fetching metrics:', error)
    }
  }

  const filteredDevices = devices.filter(device => {
    return (
      (!filters.location || device.location.toLowerCase().includes(filters.location.toLowerCase())) &&
      (!filters.user || device.username.toLowerCase().includes(filters.user.toLowerCase())) &&
      (!filters.ssid || device.wifi_ssid?.toLowerCase().includes(filters.ssid.toLowerCase()))
    )
  })

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Network Monitoring Dashboard
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
              <DeviceFilters filters={filters} setFilters={setFilters} />
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
              <DeviceList 
                devices={filteredDevices}
                selectedDevice={selectedDevice}
                onDeviceSelect={setSelectedDevice}
                onRefresh={fetchDevices}
              />
            </Paper>
          </Grid>

          {selectedDevice && (
            <>
              <Grid item xs={12} md={4}>
                <NetworkQualityCard device={selectedDevice} />
              </Grid>
              
              <Grid item xs={12} md={8}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Network Metrics Over Time
                  </Typography>
                  <Box sx={{ height: 300 }}>
                    <LineChart
                      width={600}
                      height={300}
                      data={metrics}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()}
                      />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip
                        labelFormatter={(timestamp) => new Date(timestamp).toLocaleString()}
                      />
                      <Legend />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="signal_strength"
                        stroke="#8884d8"
                        name="Signal Strength (dBm)"
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="download_speed"
                        stroke="#82ca9d"
                        name="Download Speed (Mbps)"
                      />
                    </LineChart>
                  </Box>
                </Paper>
              </Grid>
            </>
          )}
        </Grid>
      </Container>
    </ThemeProvider>
  )
}

export default App