import { Box, TextField, Typography, Button } from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'

const DeviceFilters = ({ filters, setFilters, onSearch }) => {
  const handleFilterChange = (field) => (event) => {
    setFilters(prev => ({
      ...prev,
      [field]: event.target.value
    }))
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Filters
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          label="Location"
          value={filters.location}
          onChange={handleFilterChange('location')}
          size="small"
          fullWidth
        />
        <TextField
          label="User"
          value={filters.user}
          onChange={handleFilterChange('user')}
          size="small"
          fullWidth
        />
        <TextField
          label="Wi-Fi SSID"
          value={filters.ssid}
          onChange={handleFilterChange('ssid')}
          size="small"
          fullWidth
        />
      </Box>
      <Box sx={{ mt: 2 }}>
        <Button
          variant="contained"
          startIcon={<SearchIcon />}
          onClick={onSearch}
          fullWidth
        >
          Search
        </Button>
      </Box>
    </Box>
  )
}

export default DeviceFilters