import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, IconButton, Menu, MenuItem, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button } from '@mui/material'
import { styled } from '@mui/material/styles'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import { useState } from 'react'

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  '&:nth-of-type(odd)': {
    backgroundColor: theme.palette.action.hover,
  },
  '&.selected': {
    backgroundColor: theme.palette.action.selected,
  },
  cursor: 'pointer',
}))

const DeviceList = ({ devices, selectedDevice, onDeviceSelect, onRefresh }) => {
  const [anchorEl, setAnchorEl] = useState(null)
  const [selectedMenu, setSelectedMenu] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleMenuClick = (event, device) => {
    event.stopPropagation()
    setAnchorEl(event.currentTarget)
    setSelectedMenu(device)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
    setSelectedMenu(null)
  }

  const handleSpeedTest = async () => {
    if (!selectedMenu) return
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:5000/api/devices/${selectedMenu.id}/speedtest`, {
        method: 'POST'
      })
      const data = await response.json()
      if (data.error) {
        alert(`Speed test failed: ${data.error}`)
      } else {
        alert(`Speed test results:\nDownload: ${data.download} Mbps\nUpload: ${data.upload} Mbps`)
      }
    } catch (error) {
      alert('Failed to run speed test')
    } finally {
      setLoading(false)
      handleMenuClose()
    }
  }

  const handleDelete = async () => {
    if (!selectedMenu) return
    try {
      const response = await fetch(`http://localhost:5000/api/devices/${selectedMenu.id}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        // Call the onRefresh prop to update the device list
        onRefresh()
      } else {
        alert('Failed to delete device')
      }
    } catch (error) {
      alert('Failed to delete device')
    }
    setConfirmDelete(false)
    handleMenuClose()
  }

  const getStatusColor = (status) => {
    return status === 'online' ? 'success' : 'error'
  }

  const getSignalQuality = (strength) => {
    if (!strength) return 'unknown'
    const value = parseInt(strength)
    if (value >= -50) return 'excellent'
    if (value >= -60) return 'good'
    if (value >= -70) return 'fair'
    return 'poor'
  }

  const getSignalChipColor = (quality) => {
    switch (quality) {
      case 'excellent': return 'success'
      case 'good': return 'info'
      case 'fair': return 'warning'
      case 'poor': return 'error'
      default: return 'default'
    }
  }

  return (
    <TableContainer>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Status</TableCell>
            <TableCell>Device Name</TableCell>
            <TableCell>User</TableCell>
            <TableCell>Location</TableCell>
            <TableCell>Connection</TableCell>
            <TableCell>Signal</TableCell>
            <TableCell>Last Seen (PHT)</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {devices.map((device) => (
            <StyledTableRow
              key={device.id}
              onClick={() => onDeviceSelect(device)}
              className={selectedDevice?.id === device.id ? 'selected' : ''}
            >
              <TableCell>
                <Chip
                  label={device.status}
                  color={getStatusColor(device.status)}
                  size="small"
                />
              </TableCell>
              <TableCell>{device.hostname}</TableCell>
              <TableCell>{device.username}</TableCell>
              <TableCell>{device.location}</TableCell>
              <TableCell>
                {device.connection_type}
                {device.wifi_ssid && (
                  <div style={{ fontSize: '0.8em', color: 'gray' }}>
                    {device.wifi_ssid}
                  </div>
                )}
              </TableCell>
              <TableCell>
                {device.signal_strength ? (
                  <Chip
                    label={`${device.signal_strength} (${getSignalQuality(device.signal_strength)})`}
                    color={getSignalChipColor(getSignalQuality(device.signal_strength))}
                    size="small"
                  />
                ) : (
                  'N/A'
                )}
              </TableCell>
              <TableCell>
                {new Date(device.last_seen).toLocaleString('en-PH', {
                  timeZone: 'Asia/Manila',
                  hour12: true
                })}
              </TableCell>
              <TableCell>
                <IconButton
                  size="small"
                  onClick={(e) => handleMenuClick(e, device)}
                  disabled={loading}
                >
                  <MoreVertIcon />
                </IconButton>
              </TableCell>
            </StyledTableRow>
          ))}
        </TableBody>
      </Table>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleSpeedTest} disabled={loading}>
          Run Speed Test
        </MenuItem>
        <MenuItem onClick={() => setConfirmDelete(true)}>
          Delete Device
        </MenuItem>
      </Menu>

      <Dialog
        open={confirmDelete}
        onClose={() => setConfirmDelete(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this device? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDelete(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </TableContainer>
  )
}

export default DeviceList