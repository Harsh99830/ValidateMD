import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  Paper,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  useTheme,
  useMediaQuery,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  CheckCircleOutline as CheckCircleOutlineIcon,
  ErrorOutline as ErrorOutlineIcon,
  WarningAmber as WarningAmberIcon,
  Refresh as RefreshIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  InfoOutlined as InfoOutlinedIcon
} from '@mui/icons-material';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

// Mock data - replace with actual API calls
const generateMockData = () => ({
  totalProviders: 1245,
  validatedProviders: 987,
  pendingReview: 258,
  dataAccuracy: 0.85,
  extractionAccuracy: 0.87,
  validationTrend: [
    { day: 'Mon', success: 82, total: 100 },
    { day: 'Tue', success: 88, total: 100 },
    { day: 'Wed', success: 76, total: 100 },
    { day: 'Thu', success: 91, total: 100 },
    { day: 'Fri', success: 85, total: 100 },
    { day: 'Sat', success: 79, total: 100 },
    { day: 'Sun', success: 83, total: 100 },
  ],
  providerDistribution: [
    { name: 'Primary Care', value: 420 },
    { name: 'Specialists', value: 300 },
    { name: 'Hospitals', value: 200 },
    { name: 'Labs', value: 150 },
    { name: 'Other', value: 175 },
  ],
  recentActivities: [
    { 
      id: 1, 
      type: 'validation', 
      provider: 'Dr. Sarah Johnson', 
      specialty: 'Cardiology',
      status: 'success', 
      time: '2 min ago',
      details: 'Profile validation completed successfully'
    },
    { 
      id: 2, 
      type: 'extraction', 
      provider: 'Dr. Michael Chen', 
      specialty: 'Dermatology',
      status: 'warning', 
      time: '15 min ago',
      details: 'Partial data extracted, manual review required'
    },
    { 
      id: 3, 
      type: 'validation', 
      provider: 'Dr. Emily Wilson', 
      specialty: 'Pediatrics',
      status: 'success', 
      time: '32 min ago',
      details: 'All credentials verified and validated'
    },
    { 
      id: 4, 
      type: 'extraction', 
      provider: 'Dr. Robert Taylor', 
      specialty: 'Orthopedics',
      status: 'error', 
      time: '1 hour ago',
      details: 'Failed to extract license information'
    },
    { 
      id: 5, 
      type: 'validation', 
      provider: 'Dr. Lisa Wong', 
      specialty: 'Neurology',
      status: 'success', 
      time: '2 hours ago',
      details: 'Provider information updated successfully'
    },
  ],
  systemMetrics: {
    uptime: '99.95%',
    responseTime: '1.2s',
    processingSpeed: '4.3 min/100',
    errorRate: '0.8%',
    apiCalls: '1,248',
    dataProcessed: '2.4GB'
  },
  dataQuality: {
    completeness: 92,
    accuracy: 88,
    consistency: 85,
    timeliness: 90
  }
});

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 shadow-lg rounded border border-gray-200">
        <p className="font-medium">{label}</p>
        <p className="text-sm">Success: {payload[0].value}%</p>
        <p className="text-sm text-gray-500">Total: {payload[0].payload.total} records</p>
      </div>
    );
  }
  return null;
};

const StatusIcon = ({ status }) => {
  switch (status) {
    case 'success':
      return <CheckCircleOutlineIcon color="success" fontSize="small" />;
    case 'warning':
      return <WarningAmberIcon color="warning" fontSize="small" />;
    case 'error':
      return <ErrorOutlineIcon color="error" fontSize="small" />;
    default:
      return null;
  }
};

const DashboardPage = () => {
  const [data, setData] = useState(generateMockData());
  const [loading, setLoading] = useState(true);
  
  // Calculate time saved metrics
  useEffect(() => {
    if (data) {
      const lastMonthVolume = Math.round(data.monthlyValidationVolume * 0.95); // 5% less than current
      const lastYearVolume = Math.round(data.monthlyValidationVolume * 0.8); // 20% less than current
      
      setData(prev => ({
        ...prev,
        lastMonthTimeSaved: Math.round((lastMonthVolume * data.avgTimeSavedPerProvider) / 60),
        lastYearTimeSaved: Math.round((lastYearVolume * data.avgTimeSavedPerProvider) / 60)
      }));
    }
  }, [data?.monthlyValidationVolume, data?.avgTimeSavedPerProvider]);
  const [dashboardData, setDashboardData] = useState(generateMockData());
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'lg'));

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setDashboardData(generateMockData());
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setDashboardData(generateMockData());
      setLoading(false);
    }, 800);
  };

  const validationRate = (dashboardData.validatedProviders / dashboardData.totalProviders) * 100;
  const pendingPercentage = (dashboardData.pendingReview / dashboardData.totalProviders) * 100;
  
  const getTrendIcon = (current, previous) => {
    if (current > previous) return <ArrowUpwardIcon color="success" fontSize="small" />;
    if (current < previous) return <ArrowDownwardIcon color="error" fontSize="small" />;
    return <span style={{ width: 16, height: 16, display: 'inline-block' }} />;
  };
  
  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '80vh',
        flexDirection: 'column',
        gap: 2
      }}>
        <CircularProgress size={60} thickness={4} />
        <Typography color="textSecondary">Loading dashboard data...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      p: isMobile ? 2 : 3, 
      backgroundColor: '#f9fafb', 
      minHeight: '100vh',
      maxWidth: '100%',
      mx: 'auto',
      px: { xs: 2, sm: 3, md: 4 }
    }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 3,
        flexWrap: 'wrap',
        gap: 2,
        maxWidth: 1600,
        mx: 'auto',
        width: '100%'
      }}>
        <Box>
          <Typography variant="h4" sx={{ fontSize: { xs: '1.5rem', sm: '1.8rem', md: '2.125rem' } }}>
            Provider Data Validation Dashboard
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Overview of provider data validation and system performance
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Refresh data">
            <IconButton 
              onClick={handleRefresh} 
              size="small" 
              sx={{ 
                backgroundColor: theme.palette.grey[100],
                '&:hover': { backgroundColor: theme.palette.grey[200] }
              }}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Typography variant="caption" color="textSecondary">
            Updated: {new Date().toLocaleTimeString()}
          </Typography>
        </Box>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={2} sx={{ mb: 3, justifyContent: 'center', gap: 6 }}>
        {/* Total Providers */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', borderRadius: 2, boxShadow: 1, '&:hover': { boxShadow: 3 } }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                <Typography color="textSecondary" variant="body2" fontWeight={500}>
                  TOTAL PROVIDERS
                </Typography>
                <Box sx={{ 
                  backgroundColor: theme.palette.primary.light, 
                  borderRadius: '50%',
                  width: 36,
                  height: 36,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme.palette.primary.contrastText
                }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12Z" fill="currentColor" />
                    <path d="M12 14.5C6.99 14.5 3 18.49 3 23.5C3 23.78 3.22 24 3.5 24H20.5C20.78 24 21 23.78 21 23.5C21 18.49 17.01 14.5 12 14.5Z" fill="currentColor" />
                  </svg>
                </Box>
              </Box>
              <Box display="flex" alignItems="flex-end" mb={1}>
                <Typography variant="h4" fontWeight={600} sx={{ lineHeight: 1 }}>
                  {dashboardData.totalProviders.toLocaleString()}
                </Typography>
                <Box display="flex" alignItems="center" ml={1} mb={0.5}>
                  <ArrowUpwardIcon color="success" fontSize="small" />
                  <Typography variant="caption" color="success.main" fontWeight={500}>
                    5.2%
                  </Typography>
                </Box>
              </Box>
              <Typography variant="caption" color="textSecondary">
                <Box component="span" sx={{ color: 'success.main' }}>+12.5% </Box>
                vs last month
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Validated Providers */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', borderRadius: 2, boxShadow: 1, '&:hover': { boxShadow: 3 } }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                <Typography color="textSecondary" variant="body2" fontWeight={500}>
                  VALIDATED
                </Typography>
                <Box sx={{ 
                  backgroundColor: 'rgba(46, 125, 50, 0.1)', 
                  borderRadius: '50%',
                  width: 36,
                  height: 36,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme.palette.success.main
                }}>
                  <CheckCircleOutlineIcon fontSize="small" />
                </Box>
              </Box>
              <Box display="flex" alignItems="flex-end" mb={1}>
                <Typography variant="h4" fontWeight={600} sx={{ lineHeight: 1 }}>
                  {dashboardData.validatedProviders.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="textSecondary" ml={1} mb={0.5}>
                  ({validationRate.toFixed(1)}%)
                </Typography>
              </Box>
              <Box sx={{ width: '100%', mb: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={validationRate} 
                  color={validationRate > 80 ? 'success' : 'warning'}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="caption" color="textSecondary">
                  Target: 90%
                </Typography>
                <Typography variant="caption" color={validationRate >= 80 ? 'success.main' : 'warning.main'}>
                  {validationRate >= 80 ? 'On Track' : 'Needs Attention'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Pending Review */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', borderRadius: 2, boxShadow: 1, '&:hover': { boxShadow: 3 } }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                <Typography color="textSecondary" variant="body2" fontWeight={500}>
                  PENDING REVIEW
                </Typography>
                <Box sx={{ 
                  backgroundColor: 'rgba(255, 167, 38, 0.1)', 
                  borderRadius: '50%',
                  width: 36,
                  height: 36,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme.palette.warning.main
                }}>
                  <WarningAmberIcon fontSize="small" />
                </Box>
              </Box>
              <Box display="flex" alignItems="flex-end" mb={1}>
                <Typography variant="h4" fontWeight={600} sx={{ lineHeight: 1 }}>
                  {dashboardData.pendingReview}
                </Typography>
                <Typography variant="body2" color="textSecondary" ml={1} mb={0.5}>
                  ({pendingPercentage.toFixed(1)}%)
                </Typography>
              </Box>
              <Box display="flex" alignItems="center" mb={0.5}>
                <Box sx={{ flex: 1, mr: 1 }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={pendingPercentage} 
                    color="warning"
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
                <Typography variant="caption" color="textSecondary">
                  {pendingPercentage > 10 ? 'High' : 'Low'} priority
                </Typography>
              </Box>
              <Typography variant="caption" color="textSecondary">
                {dashboardData.recentActivities.filter(a => a.status === 'warning' || a.status === 'error').length} new issues
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Data Accuracy */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', borderRadius: 2, boxShadow: 1, '&:hover': { boxShadow: 3 } }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                <Typography color="textSecondary" variant="body2" fontWeight={500}>
                  DATA ACCURACY
                </Typography>
                <Box sx={{ 
                  backgroundColor: 'rgba(63, 81, 181, 0.1)', 
                  borderRadius: '50%',
                  width: 36,
                  height: 36,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme.palette.primary.main
                }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" fill="currentColor" />
                  </svg>
                </Box>
              </Box>
              <Box display="flex" alignItems="center" mb={2}>
                <Typography variant="h2" fontWeight={600} sx={{ lineHeight: 1 }}>
                  {(dashboardData.dataAccuracy * 100).toFixed(0)}%
                </Typography>
                <Box display="flex" alignItems="center" ml={1} mb={0.5}>
                  {getTrendIcon(85, 82)}
                  <Typography variant="caption" color={85 > 82 ? 'success.main' : 'error.main'} fontWeight={500}>
                    {85 > 82 ? '2.3%' : '1.2%'}
                  </Typography>
                </Box>
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="caption" display="block" color="textSecondary">
                    Last Month: 82.5%
                  </Typography>
                  <Typography variant="caption" display="block" color="textSecondary">
                    Target: 90%
                  </Typography>
                </Box>
                <Box sx={{ 
                  width: 36, 
                  height: 36, 
                  borderRadius: '50%', 
                  backgroundColor: dashboardData.dataAccuracy >= 0.8 ? 'success.light' : 'warning.light',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: dashboardData.dataAccuracy >= 0.8 ? 'success.dark' : 'warning.dark'
                }}>
                  {dashboardData.dataAccuracy >= 0.8 ? '✓' : '!'}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={2} sx={{ 
        mb: 6, // Increased bottom margin
        mt: 2, // Added top margin
        justifyContent: 'center' 
      }}>
        {/* Validation Trend */}
        <Grid item xs={12} md={10} lg={8}>
          <Paper sx={{ 
            p: 2, 
            height: '100%', 
            width:'500px',
            borderRadius: 2, 
            boxShadow: 1, 
            '&:hover': { boxShadow: 3 },
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center'
          }}>
            <Box display="flex" justifyContent="center" alignItems="center" mb={2} width="100%">
              <Typography variant="h6" fontWeight={600} align="center">Validation Trend</Typography>
              <Box display="flex" alignItems="center" gap={1}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ 
                    width: 12, 
                    height: 12, 
                    bgcolor: 'success.main', 
                    borderRadius: '2px', 
                    mr: 1 
                  }} />
                  <Typography variant="caption">Success Rate</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
                  <Box sx={{ width: 12, height: 12, bgcolor: 'grey.300', borderRadius: '2px', mr: 1 }} />
                  <Typography variant="caption">Target</Typography>
                </Box>
              </Box>
            </Box>
            <Box sx={{ 
              height: 400, 
              width: '100%',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center'
            }}>
              <ResponsiveContainer width="95%" height="95%">
                <LineChart data={dashboardData.validationTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="day" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis 
                    domain={[0, 100]} 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip 
                    content={<CustomTooltip />} 
                    cursor={{ stroke: '#f0f0f0', strokeWidth: 1 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="success" 
                    stroke={theme.palette.success.main} 
                    strokeWidth={2}
                    dot={{ r: 4, fill: theme.palette.success.main, strokeWidth: 2, stroke: '#fff' }}
                    activeDot={{ r: 6, stroke: theme.palette.success.main, strokeWidth: 2, fill: '#fff' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="total" 
                    stroke="#e0e0e0" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Provider Distribution */}
        <Grid item xs={12} md={6} lg={4}>
          <Paper sx={{ 
            p: 2, 
            height: '100%', 
            borderRadius: 2, 
            boxShadow: 1, 
            '&:hover': { boxShadow: 3 },
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center'
          }}>
            <Typography variant="h6" fontWeight={600} mb={2} align="center" width="100%">Provider Distribution</Typography>
            <Box sx={{ 
              height: 400, 
              width: '100%',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center'
            }}>
              <PieChart width={Math.min(400, window.innerWidth * 0.9)} height={400}>
                <Pie
                  data={dashboardData.providerDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {dashboardData.providerDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value, name, props) => [
                    `${value} (${((value / dashboardData.totalProviders) * 100).toFixed(1)}%)`,
                    props.payload.name
                  ]}
                />
                <Legend 
                  layout="vertical"
                  verticalAlign="middle"
                  align="right"
                  formatter={(value, entry, index) => (
                    <Typography variant="caption" sx={{ ml: 1 }}>
                      {value} ({((entry.payload.value / dashboardData.totalProviders) * 100).toFixed(1)}%)
                    </Typography>
                  )}
                />
              </PieChart>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* System Metrics */}
      <Grid container spacing={2} sx={{ 
        mb: 6, // Increased bottom margin
        mt: 2, // Added top margin
        justifyContent: 'center' 
      }}>
        {Object.entries({
          'Uptime': { value: dashboardData.systemMetrics.uptime, icon: '🟢', trend: 'up', change: '0.05%' },
          'Response Time': { value: dashboardData.systemMetrics.responseTime, icon: '⚡', trend: 'down', change: '0.3s' },
          'Processing Speed': { value: dashboardData.systemMetrics.processingSpeed, icon: '⏱️', trend: 'up', change: '0.7 min' },
          'Error Rate': { 
            value: dashboardData.systemMetrics.errorRate, 
            icon: '⚠️', 
            trend: parseFloat(dashboardData.systemMetrics.errorRate) > 1 ? 'up' : 'down',
            change: '0.2%'
          },
          'API Calls': { value: dashboardData.systemMetrics.apiCalls, icon: '📊', trend: 'up', change: '12.4%' },
          'Data Processed': { value: dashboardData.systemMetrics.dataProcessed, icon: '💾', trend: 'up', change: '0.5GB' }
        }).map(([key, metric], index) => (
          <Grid item xs={12} sm={6} md={4} lg={2} key={index}>
            <Paper sx={{ p: 2, height: '100%', borderRadius: 2, boxShadow: 1, '&:hover': { boxShadow: 3 } }}>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <Box>
                  <Typography variant="caption" color="textSecondary" fontWeight={500}>
                    {key.toUpperCase()}
                  </Typography>
                  <Typography variant="h6" fontWeight={600} mt={0.5}>
                    {metric.value}
                  </Typography>
                </Box>
                <Box sx={{ 
                  width: 40,
                  height: 40,
                  borderRadius: '12px',
                  backgroundColor: 'rgba(63, 81, 181, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.2rem'
                }}>
                  {metric.icon}
                </Box>
              </Box>
              <Box display="flex" alignItems="center" mt={1}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  color: metric.trend === 'up' ? 'success.main' : 'error.main',
                  mr: 1
                }}>
                  {metric.trend === 'up' ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />}
                  <Typography variant="caption" fontWeight={500}>
                    {metric.change}
                  </Typography>
                </Box>
                <Typography variant="caption" color="textSecondary">
                  vs last week
                </Typography>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Recent Activities */}
      <Grid container spacing={2} sx={{ 
        mb: 3, // Standard bottom margin
        mt: 2  // Added top margin
      }}>
        <Grid item xs={12}>
          <Paper sx={{ 
            p: 3, // Increased padding
            borderRadius: 2, 
            boxShadow: 1, 
            '&:hover': { boxShadow: 3 },
            height: '100%',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <Box sx={{ 
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              mb: 3 // Added bottom margin to the header section
            }}>
              <Typography variant="h6" fontWeight={600}>Recent Activities</Typography>
              <Typography 
                variant="button" 
                color="primary" 
                sx={{ 
                  cursor: 'pointer',
                  '&:hover': { textDecoration: 'underline' }
                }}
              >
                View All
              </Typography>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Activity</TableCell>
                    {!isMobile && <TableCell>Provider</TableCell>}
                    {!isTablet && <TableCell>Specialty</TableCell>}
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Time</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dashboardData.recentActivities.map((activity) => (
                    <TableRow 
                      key={activity.id} 
                      hover 
                      sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                    >
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Box sx={{ 
                            width: 32, 
                            height: 32, 
                            borderRadius: '8px',
                            backgroundColor: 
                              activity.status === 'success' ? 'rgba(46, 125, 50, 0.1)' :
                              activity.status === 'warning' ? 'rgba(255, 167, 38, 0.1)' : 
                              'rgba(244, 67, 54, 0.1)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            mr: 1.5,
                            flexShrink: 0
                          }}>
                            <StatusIcon status={activity.status} />
                          </Box>
                          <Box>
                            <Typography variant="body2" fontWeight={500}>
                              {activity.type === 'validation' ? 'Data Validation' : 'Document Extraction'}
                            </Typography>
                            {isMobile && (
                              <Typography variant="caption" color="text.secondary">
                                {activity.provider}
                              </Typography>
                            )}
                            <Typography variant="caption" display="block" color="text.secondary" noWrap>
                              {activity.details}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      {!isMobile && (
                        <TableCell>
                          <Typography variant="body2">{activity.provider}</Typography>
                        </TableCell>
                      )}
                      {!isTablet && (
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {activity.specialty}
                          </Typography>
                        </TableCell>
                      )}
                      <TableCell>
                        <Box 
                          sx={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            px: 1.5,
                            py: 0.5,
                            borderRadius: 4,
                            bgcolor: 
                              activity.status === 'success' ? 'rgba(46, 125, 50, 0.1)' :
                              activity.status === 'warning' ? 'rgba(255, 167, 38, 0.1)' : 
                              'rgba(244, 67, 54, 0.1)',
                            color: 
                              activity.status === 'success' ? 'success.dark' :
                              activity.status === 'warning' ? 'warning.dark' : 'error.dark',
                            textTransform: 'capitalize',
                            fontSize: '0.7rem',
                            fontWeight: 600,
                            letterSpacing: '0.5px'
                          }}
                        >
                          {activity.status}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="text.secondary">
                          {activity.time}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
