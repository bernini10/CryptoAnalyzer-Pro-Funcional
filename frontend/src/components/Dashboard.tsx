import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
} from '@mui/material';
import {
  AccountCircle,
  Logout,
  TrendingUp,
  TrendingDown,
  Assessment,
  Notifications,
  Refresh,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';

interface DashboardProps {
  onLogout: () => void;
}

interface CryptoData {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  volume: number;
  marketCap: number;
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Mock data fetching
  const { data: cryptoData, isLoading, refetch } = useQuery(
    'cryptoData',
    async (): Promise<CryptoData[]> => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return [
        {
          symbol: 'BTC',
          name: 'Bitcoin',
          price: 67500,
          change24h: 2.4,
          volume: 28000000000,
          marketCap: 1320000000000,
        },
        {
          symbol: 'ETH',
          name: 'Ethereum',
          price: 4350,
          change24h: 3.1,
          volume: 15000000000,
          marketCap: 523000000000,
        },
        {
          symbol: 'UNI',
          name: 'Uniswap',
          price: 11.47,
          change24h: 8.7,
          volume: 245000000,
          marketCap: 8900000000,
        },
        {
          symbol: 'ADA',
          name: 'Cardano',
          price: 0.52,
          change24h: -1.2,
          volume: 180000000,
          marketCap: 18500000000,
        },
        {
          symbol: 'TAO',
          name: 'Bittensor',
          price: 425.30,
          change24h: 15.8,
          volume: 89000000,
          marketCap: 3200000000,
        },
      ];
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      onSuccess: () => {
        setLastUpdate(new Date());
      },
    }
  );

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    onLogout();
    toast.success('Logged out successfully');
  };

  const handleRefresh = () => {
    refetch();
    toast.success('Data refreshed');
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatLargeNumber = (value: number) => {
    if (value >= 1e12) {
      return `$${(value / 1e12).toFixed(2)}T`;
    } else if (value >= 1e9) {
      return `$${(value / 1e9).toFixed(2)}B`;
    } else if (value >= 1e6) {
      return `$${(value / 1e6).toFixed(2)}M`;
    }
    return formatCurrency(value);
  };

  const getPriceChangeColor = (change: number) => {
    if (change > 0) return 'success.main';
    if (change < 0) return 'error.main';
    return 'text.secondary';
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ backgroundColor: 'background.paper' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            📊 CryptoAnalyzer Pro
          </Typography>
          
          <Chip
            label={`Last Update: ${lastUpdate.toLocaleTimeString()}`}
            size="small"
            sx={{ mr: 2 }}
          />
          
          <IconButton color="inherit" onClick={handleRefresh}>
            <Refresh />
          </IconButton>
          
          <IconButton color="inherit">
            <Notifications />
          </IconButton>
          
          <IconButton
            size="large"
            edge="end"
            color="inherit"
            onClick={handleMenuOpen}
          >
            <AccountCircle />
          </IconButton>
          
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleLogout}>
              <Logout sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ p: 3 }}>
        {/* Market Overview Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Assessment sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6">Total Market Cap</Typography>
                  </Box>
                  <Typography variant="h4" color="primary.main">
                    $2.45T
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    +2.4% (24h)
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                    <Typography variant="h6">BTC Dominance</Typography>
                  </Box>
                  <Typography variant="h4" color="warning.main">
                    59.8%
                  </Typography>
                  <Typography variant="body2" color="error.main">
                    -1.2% (7d)
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <TrendingDown sx={{ mr: 1, color: 'info.main' }} />
                    <Typography variant="h6">Alt Season Index</Typography>
                  </Box>
                  <Typography variant="h4" color="success.main">
                    67
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    Alt Season Starting
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Assessment sx={{ mr: 1, color: 'secondary.main' }} />
                    <Typography variant="h6">Active Alerts</Typography>
                  </Box>
                  <Typography variant="h4" color="secondary.main">
                    12
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    3 High Priority
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>

        {/* Cryptocurrency Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Cryptocurrencies
              </Typography>
              
              {isLoading && <LinearProgress sx={{ mb: 2 }} />}
              
              <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell align="right">Price</TableCell>
                      <TableCell align="right">24h Change</TableCell>
                      <TableCell align="right">Volume</TableCell>
                      <TableCell align="right">Market Cap</TableCell>
                      <TableCell align="center">Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {cryptoData?.map((crypto, index) => (
                      <motion.tr
                        key={crypto.symbol}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                        component={TableRow}
                      >
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="body1" fontWeight={600}>
                              {crypto.symbol}
                            </Typography>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{ ml: 1 }}
                            >
                              {crypto.name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body1" fontWeight={600}>
                            {formatCurrency(crypto.price)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'flex-end',
                            }}
                          >
                            {crypto.change24h > 0 ? (
                              <TrendingUp sx={{ fontSize: 16, mr: 0.5 }} />
                            ) : (
                              <TrendingDown sx={{ fontSize: 16, mr: 0.5 }} />
                            )}
                            <Typography
                              variant="body2"
                              sx={{ color: getPriceChangeColor(crypto.change24h) }}
                            >
                              {crypto.change24h > 0 ? '+' : ''}
                              {crypto.change24h.toFixed(2)}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {formatLargeNumber(crypto.volume)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {formatLargeNumber(crypto.marketCap)}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => toast.info(`Analyzing ${crypto.symbol}...`)}
                          >
                            Analyze
                          </Button>
                        </TableCell>
                      </motion.tr>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </motion.div>
      </Box>
    </Box>
  );
};

export default Dashboard;

