import { Card, CardContent, Typography, Box, LinearProgress } from '@mui/material'
import { styled } from '@mui/material/styles'

const QualityIndicator = styled(LinearProgress)(({ theme, quality }) => ({
  height: 10,
  borderRadius: 5,
  backgroundColor: theme.palette.grey[200],
  '& .MuiLinearProgress-bar': {
    backgroundColor: {
      excellent: theme.palette.success.main,
      good: theme.palette.info.main,
      fair: theme.palette.warning.main,
      poor: theme.palette.error.main
    }[quality]
  }
}))

const MetricBox = ({ label, value, quality, unit }) => (
  <Box sx={{ mb: 2 }}>
    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
      {label}
    </Typography>
    <Typography variant="h6" component="div">
      {value} {unit}
    </Typography>
    <QualityIndicator
      variant="determinate"
      value={{
        excellent: 100,
        good: 75,
        fair: 50,
        poor: 25
      }[quality]}
      quality={quality}
    />
  </Box>
)

const NetworkQualityCard = ({ device }) => {
  const getSignalQuality = (strength) => {
    if (!strength) return 'poor'
    const value = parseInt(strength)
    if (value >= -50) return 'excellent'
    if (value >= -60) return 'good'
    if (value >= -70) return 'fair'
    return 'poor'
  }

  const getLatencyQuality = (latency) => {
    if (!latency) return 'poor'
    if (latency < 50) return 'excellent'
    if (latency < 100) return 'good'
    if (latency < 150) return 'fair'
    return 'poor'
  }

  const getSpeedQuality = (speed) => {
    if (!speed) return 'poor'
    if (speed >= 100) return 'excellent'
    if (speed >= 50) return 'good'
    if (speed >= 25) return 'fair'
    return 'poor'
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Network Quality Metrics
        </Typography>

        <MetricBox
          label="Signal Strength"
          value={device.signal_strength?.split(' ')[0] || 'N/A'}
          unit="dBm"
          quality={getSignalQuality(device.signal_strength)}
        />

        <MetricBox
          label="Latency"
          value={device.latency || 'N/A'}
          unit="ms"
          quality={getLatencyQuality(device.latency)}
        />

        <MetricBox
          label="Download Speed"
          value={device.download_speed || 'N/A'}
          unit="Mbps"
          quality={getSpeedQuality(device.download_speed)}
        />

        <MetricBox
          label="Upload Speed"
          value={device.upload_speed || 'N/A'}
          unit="Mbps"
          quality={getSpeedQuality(device.upload_speed)}
        />
      </CardContent>
    </Card>
  )
}

export default NetworkQualityCard