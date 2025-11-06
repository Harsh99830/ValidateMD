import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Grid,
  LinearProgress,
  Card,
  CardContent
} from '@mui/material';

// Mock data - replace with actual API calls
const validationData = {
  totalProcessed: 200,
  successRate: 0.82,
  averageConfidence: 0.88,
  extractionAccuracy: 0.87,
  processingSpeed: '4.5 minutes',
  commonIssues: [
    { name: 'Missing Phone', count: 24 },
    { name: 'Outdated Address', count: 18 },
    { name: 'Incomplete Credentials', count: 12 },
    { name: 'License Expired', count: 8 },
  ],
  providers: Array(10).fill().map((_, i) => ({
    id: i + 1,
    name: `Provider ${i + 1}`,
    npi: `12345${i}6789`,
    specialty: ['Cardiology', 'Dermatology', 'Pediatrics'][i % 3],
    confidence: 0.7 + (i * 0.03),
    status: i % 5 === 0 ? 'Needs Review' : 'Validated',
    lastValidated: new Date(Date.now() - i * 3600000).toLocaleString()
  }))
};

const ValidationReport = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Validation Report</Typography>
      
      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Processed</Typography>
              <Typography variant="h5">{validationData.totalProcessed}</Typography>
              <Typography variant="caption" color="textSecondary">providers</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Validation Success Rate</Typography>
              <Typography variant="h5">{(validationData.successRate * 100).toFixed(1)}%</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ width: '100%', mr: 1 }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={validationData.successRate * 100} 
                    color={validationData.successRate >= 0.8 ? 'success' : 'warning'}
                  />
                </Box>
                <Typography variant="body2" color="textSecondary">
                  {validationData.successRate >= 0.8 ? 'On Target' : 'Needs Improvement'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Avg. Confidence</Typography>
              <Typography variant="h5">{(validationData.averageConfidence * 100).toFixed(1)}%</Typography>
              <Typography variant="caption" color="textSecondary">across all fields</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Processing Speed</Typography>
              <Typography variant="h5">{validationData.processingSpeed}</Typography>
              <Typography variant="caption" color="textSecondary">per 100 providers</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Data Quality Issues */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Common Data Quality Issues</Typography>
            {validationData.commonIssues.map((issue) => (
              <Box key={issue.name} sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">{issue.name}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {issue.count} cases ({(issue.count / validationData.totalProcessed * 100).toFixed(1)}%)
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={(issue.count / validationData.totalProcessed) * 100} 
                  sx={{ height: 8, borderRadius: 1 }}
                />
              </Box>
            ))}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Extraction Accuracy</Typography>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Box 
                sx={{
                  width: 150,
                  height: 150,
                  margin: '0 auto',
                  borderRadius: '50%',
                  background: `conic-gradient(
                    #4caf50 ${validationData.extractionAccuracy * 100}%, 
                    #e0e0e0 ${validationData.extractionAccuracy * 100}% 100%
                  )`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mb: 2
                }}
              >
                <Box
                  sx={{
                    width: '80%',
                    height: '80%',
                    backgroundColor: 'white',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexDirection: 'column'
                  }}
                >
                  <Typography variant="h4">
                    {(validationData.extractionAccuracy * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="caption" color="textSecondary">Accuracy</Typography>
                </Box>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Document extraction success rate
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Provider List */}
      <Paper sx={{ p: 2, mb: 4 }}>
        <Typography variant="h6" gutterBottom>Provider Validation Status</Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Provider Name</TableCell>
                <TableCell>NPI</TableCell>
                <TableCell>Specialty</TableCell>
                <TableCell>Confidence</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last Validated</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {validationData.providers.map((provider) => (
                <TableRow key={provider.id} hover>
                  <TableCell>{provider.name}</TableCell>
                  <TableCell>{provider.npi}</TableCell>
                  <TableCell>{provider.specialty}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={provider.confidence * 100} 
                          color={
                            provider.confidence > 0.85 ? 'success' : 
                            provider.confidence > 0.7 ? 'warning' : 'error'
                          }
                        />
                      </Box>
                      <Typography variant="body2" color="textSecondary">
                        {(provider.confidence * 100).toFixed(0)}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box 
                      sx={{
                        display: 'inline-block',
                        px: 1,
                        py: 0.5,
                        borderRadius: 1,
                        backgroundColor: provider.status === 'Validated' ? '#e8f5e9' : '#fff3e0',
                        color: provider.status === 'Validated' ? '#2e7d32' : '#e65100',
                        fontSize: '0.75rem',
                        fontWeight: 500
                      }}
                    >
                      {provider.status}
                    </Box>
                  </TableCell>
                  <TableCell>{provider.lastValidated}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default ValidationReport;
