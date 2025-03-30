import React, { useState, useEffect } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Typography,
  Grid,
  Paper,
  Divider,
  Card,
  CardContent,
  CardActions,
  CardMedia,
  Chip,
  IconButton,
  LinearProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Schedule as ScheduleIcon,
  Comment as CommentIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';
import { Artwork } from '../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

const Dashboard: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [artworks, setArtworks] = useState<Artwork[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    totalArtworks: 0,
    totalViews: 0,
    totalReveals: 0,
    totalComments: 0,
  });

  // Redirect if not authenticated or not an artist
  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user?.is_artist)) {
      navigate('/');
    }
  }, [isLoading, isAuthenticated, user, navigate]);

  // Fetch artist's artworks and stats
  useEffect(() => {
    const fetchData = async () => {
      if (isAuthenticated && user?.is_artist) {
        try {
          setLoading(true);
          
          // Fetch artist's artworks
          const artworksResponse = await apiService.artworks.getMyArtworks();
          setArtworks(artworksResponse);
          
          // Calculate stats
          const totalArtworks = artworksResponse.length;
          const totalViews = artworksResponse.reduce((sum, artwork) => sum + artwork.view_count, 0);
          const totalReveals = artworksResponse.filter(a => a.is_revealed).length;
          const totalComments = artworksResponse.reduce((sum, artwork) => sum + artwork.comments.length, 0);
          
          setStats({
            totalArtworks,
            totalViews,
            totalReveals,
            totalComments,
          });
          
          setError(null);
        } catch (err) {
          setError(
            err instanceof Error ? err.message : 'Failed to load dashboard data. Please try again.'
          );
        } finally {
          setLoading(false);
        }
      }
    };
    
    fetchData();
  }, [isAuthenticated, user]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Delete artwork handler
  const handleDeleteArtwork = async (artworkId: number) => {
    if (window.confirm('Are you sure you want to delete this artwork? This action cannot be undone.')) {
      try {
        await apiService.artworks.delete(artworkId);
        
        // Update artworks list
        setArtworks(artworks.filter(artwork => artwork.id !== artworkId));
        
        // Update stats
        const deletedArtwork = artworks.find(artwork => artwork.id === artworkId);
        if (deletedArtwork) {
          setStats(prevStats => ({
            totalArtworks: prevStats.totalArtworks - 1,
            totalViews: prevStats.totalViews - deletedArtwork.view_count,
            totalReveals: deletedArtwork.is_revealed ? prevStats.totalReveals - 1 : prevStats.totalReveals,
            totalComments: prevStats.totalComments - deletedArtwork.comments.length,
          }));
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to delete artwork. Please try again.'
        );
      }
    }
  };

  // Format reveal condition for display
  const formatRevealCondition = (artwork: Artwork) => {
    if (artwork.is_revealed) {
      return <Chip label="Revealed" color="success" size="small" icon={<VisibilityIcon />} />;
    }
    
    const condition = artwork.reveal_conditions[0];
    if (!condition) return 'Unknown';
    
    switch (condition.condition_type) {
      case 'time':
        const revealDate = new Date(condition.condition_value.reveal_at);
        return (
          <Chip 
            label={`Reveals on ${revealDate.toLocaleDateString()}`} 
            color="primary" 
            size="small" 
            icon={<ScheduleIcon />} 
          />
        );
      case 'view_count':
        const progress = (artwork.view_count / condition.condition_value.count) * 100;
        return (
          <Box>
            <Chip 
              label={`${artwork.view_count}/${condition.condition_value.count} views`} 
              color="primary" 
              size="small" 
              icon={<VisibilityIcon />} 
            />
            <LinearProgress 
              variant="determinate" 
              value={Math.min(progress, 100)} 
              sx={{ mt: 1, height: 6, borderRadius: 3 }} 
            />
          </Box>
        );
      case 'interactive':
        const commentProgress = (artwork.comments.length / condition.condition_value.comment_count) * 100;
        return (
          <Box>
            <Chip 
              label={`${artwork.comments.length}/${condition.condition_value.comment_count} comments`} 
              color="primary" 
              size="small" 
              icon={<CommentIcon />} 
            />
            <LinearProgress 
              variant="determinate" 
              value={Math.min(commentProgress, 100)} 
              sx={{ mt: 1, height: 6, borderRadius: 3 }} 
            />
          </Box>
        );
      default:
        return 'Custom condition';
    }
  };

  if (isLoading) {
    return (
      <Container sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Artist Dashboard
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <Typography variant="h6" color="text.secondary">
              Total Artworks
            </Typography>
            <Typography variant="h3" sx={{ mt: 2, mb: 0 }}>
              {stats.totalArtworks}
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <Typography variant="h6" color="text.secondary">
              Total Views
            </Typography>
            <Typography variant="h3" sx={{ mt: 2, mb: 0 }}>
              {stats.totalViews}
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <Typography variant="h6" color="text.secondary">
              Revealed Artworks
            </Typography>
            <Typography variant="h3" sx={{ mt: 2, mb: 0 }}>
              {stats.totalReveals} / {stats.totalArtworks}
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <Typography variant="h6" color="text.secondary">
              Total Comments
            </Typography>
            <Typography variant="h3" sx={{ mt: 2, mb: 0 }}>
              {stats.totalComments}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Upload button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          component={RouterLink}
          to="/upload"
        >
          Upload New Artwork
        </Button>
      </Box>
      
      {/* Tabs */}
      <Box sx={{ width: '100%', bgcolor: 'background.paper', mb: 4 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          indicatorColor="primary"
          textColor="primary"
          centered
        >
          <Tab label="My Artworks" id="dashboard-tab-0" />
          <Tab label="Analytics" id="dashboard-tab-1" />
        </Tabs>
        
        {/* My Artworks Tab */}
        <TabPanel value={tabValue} index={0}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : artworks.length > 0 ? (
            <Grid container spacing={3}>
              {artworks.map((artwork) => (
                <Grid item key={artwork.id} xs={12} sm={6} md={4}>
                  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardMedia
                      component="img"
                      height="140"
                      image={artwork.is_revealed ? artwork.image_url : artwork.placeholder_image || '/placeholder.jpg'}
                      alt={artwork.title}
                      sx={{ 
                        objectFit: 'cover',
                        filter: artwork.is_revealed ? 'none' : 'blur(0px) brightness(0.7)'
                      }}
                    />
                    
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Typography variant="h6" component="h2" gutterBottom>
                          {artwork.title}
                        </Typography>
                        
                        <IconButton size="small" sx={{ mt: -1, mr: -1 }}>
                          <MoreVertIcon />
                        </IconButton>
                      </Box>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        {artwork.is_revealed ? (
                          <Chip icon={<VisibilityIcon />} label="Revealed" color="success" size="small" />
                        ) : (
                          <Chip icon={<VisibilityOffIcon />} label="Hidden" color="default" size="small" />
                        )}
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {artwork.description?.substring(0, 120)}
                        {artwork.description && artwork.description.length > 120 ? '...' : ''}
                      </Typography>
                      
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Reveal Condition:
                        </Typography>
                        {formatRevealCondition(artwork)}
                      </Box>
                      
                      <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                        <Chip
                          icon={<VisibilityIcon />}
                          label={`${artwork.view_count} views`}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          icon={<CommentIcon />}
                          label={`${artwork.comments.length} comments`}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    </CardContent>
                    
                    <CardActions>
                      <Button 
                        size="small" 
                        component={RouterLink} 
                        to={`/artwork/${artwork.id}`}
                      >
                        View
                      </Button>
                      <Button 
                        size="small" 
                        startIcon={<EditIcon />}
                        component={RouterLink} 
                        to={`/edit-artwork/${artwork.id}`}
                      >
                        Edit
                      </Button>
                      <Button 
                        size="small" 
                        color="error" 
                        startIcon={<DeleteIcon />}
                        onClick={() => handleDeleteArtwork(artwork.id)}
                      >
                        Delete
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" paragraph>
                You haven't uploaded any artworks yet.
              </Typography>
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                component={RouterLink}
                to="/upload"
              >
                Upload Your First Artwork
              </Button>
            </Paper>
          )}
        </TabPanel>
        
        {/* Analytics Tab */}
        <TabPanel value={tabValue} index={1}>
          <Paper>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Artwork</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Views</TableCell>
                    <TableCell align="right">Comments</TableCell>
                    <TableCell align="right">Completion</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        <CircularProgress size={30} sx={{ my: 3 }} />
                      </TableCell>
                    </TableRow>
                  ) : artworks.length > 0 ? (
                    artworks.map((artwork) => {
                      // Calculate completion percentage based on reveal condition
                      let completionPercentage = artwork.is_revealed ? 100 : 0;
                      
                      if (!artwork.is_revealed && artwork.reveal_conditions[0]) {
                        const condition = artwork.reveal_conditions[0];
                        
                        switch (condition.condition_type) {
                          case 'time':
                            const revealDate = new Date(condition.condition_value.reveal_at);
                            const totalDuration = revealDate.getTime() - new Date(artwork.created_at).getTime();
                            const elapsedDuration = Date.now() - new Date(artwork.created_at).getTime();
                            completionPercentage = Math.min(100, Math.floor((elapsedDuration / totalDuration) * 100));
                            break;
                          case 'view_count':
                            completionPercentage = Math.min(100, Math.floor((artwork.view_count / condition.condition_value.count) * 100));
                            break;
                          case 'interactive':
                            completionPercentage = Math.min(100, Math.floor((artwork.comments.length / condition.condition_value.comment_count) * 100));
                            break;
                        }
                      }
                      
                      return (
                        <TableRow key={artwork.id} hover>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Box
                                component="img"
                                src={artwork.is_revealed ? artwork.image_url : artwork.placeholder_image || '/placeholder.jpg'}
                                alt={artwork.title}
                                sx={{ 
                                  width: 60, 
                                  height: 60, 
                                  borderRadius: 1,
                                  objectFit: 'cover',
                                  mr: 2,
                                  filter: artwork.is_revealed ? 'none' : 'blur(0px) brightness(0.7)'
                                }}
                              />
                              <Typography variant="subtitle2">
                                {artwork.title}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            {artwork.is_revealed ? (
                              <Chip icon={<VisibilityIcon />} label="Revealed" color="success" size="small" />
                            ) : (
                              <Chip icon={<VisibilityOffIcon />} label="Hidden" color="default" size="small" />
                            )}
                          </TableCell>
                          <TableCell align="right">{artwork.view_count}</TableCell>
                          <TableCell align="right">{artwork.comments.length}</TableCell>
                          <TableCell align="right">
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <LinearProgress
                                variant="determinate"
                                value={completionPercentage}
                                sx={{ flex: 1, mr: 1, height: 6, borderRadius: 3 }}
                              />
                              <Typography variant="caption">
                                {completionPercentage}%
                              </Typography>
                            </Box>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  ) : (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        <Typography variant="subtitle1" sx={{ py: 3 }}>
                          No artworks to analyze
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </TabPanel>
      </Box>
    </Container>
  );
};

export default Dashboard; 