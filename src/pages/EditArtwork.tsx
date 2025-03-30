import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  FormHelperText,
  Stack,
} from '@mui/material';
import { CloudUpload as CloudUploadIcon, Save as SaveIcon } from '@mui/icons-material';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';
import { Artwork, RevealCondition } from '../types';

// Validation schema
const editArtworkSchema = Yup.object().shape({
  title: Yup.string()
    .required('Title is required')
    .max(255, 'Title must be less than 255 characters'),
  description: Yup.string()
    .max(1000, 'Description must be less than 1000 characters'),
  placeholder_image: Yup.mixed(),
});

const EditArtwork: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const artworkId = Number(id);
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const [artwork, setArtwork] = useState<Artwork | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [placeholder, setPlaceholder] = useState<File | null>(null);
  const [placeholderPreview, setPlaceholderPreview] = useState<string | null>(null);

  // Fetch artwork data
  useEffect(() => {
    const fetchArtwork = async () => {
      try {
        setLoading(true);
        const artworkData = await apiService.artworks.getById(artworkId);
        
        // Check if the logged-in user is the owner of this artwork
        if (isAuthenticated && user?.id !== artworkData.user.id) {
          setError("You don't have permission to edit this artwork");
          navigate('/gallery');
          return;
        }
        
        setArtwork(artworkData);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to load artwork. Please try again.'
        );
        navigate('/not-found');
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated && !isLoading) {
      fetchArtwork();
    }
  }, [isAuthenticated, isLoading, user, artworkId, navigate]);

  // Redirect if not authenticated or not an artist
  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user?.is_artist)) {
      navigate('/gallery');
    }
  }, [isLoading, isAuthenticated, user, navigate]);

  // Handle placeholder image change
  const handlePlaceholderChange = (event: React.ChangeEvent<HTMLInputElement>, setFieldValue: any) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setPlaceholder(file);
      setFieldValue('placeholder_image', file);
      
      // Generate preview
      const reader = new FileReader();
      reader.onload = () => {
        setPlaceholderPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle form submission
  const handleSubmit = async (values: any, { setSubmitting }: any) => {
    setSaving(true);
    setSuccess(false);
    setError(null);
    
    try {
      // Prepare artwork update data
      const artworkData = {
        title: values.title,
        description: values.description,
        placeholder_image: values.placeholder_image,
      };
      
      // Update artwork
      await apiService.artworks.update(artworkId, artworkData);
      
      setSuccess(true);
      
      // Redirect back to artwork page after a delay
      setTimeout(() => {
        navigate(`/artwork/${artworkId}`);
      }, 2000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to update artwork. Please try again.'
      );
    } finally {
      setSaving(false);
      setSubmitting(false);
    }
  };

  // Show loading state
  if (isLoading || loading) {
    return (
      <Container sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
      </Container>
    );
  }

  // Show error if artwork not found or permission denied
  if (error || !artwork) {
    return (
      <Container sx={{ py: 8 }}>
        <Alert severity="error" sx={{ mb: 4 }}>
          {error || "Artwork not found"}
        </Alert>
        <Button variant="contained" onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Edit Artwork
      </Typography>
      
      <Divider sx={{ my: 4 }} />
      
      {success && (
        <Alert severity="success" sx={{ mb: 4 }}>
          Artwork updated successfully! Redirecting...
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      <Formik
        initialValues={{
          title: artwork.title,
          description: artwork.description || '',
          placeholder_image: null,
        }}
        validationSchema={editArtworkSchema}
        onSubmit={handleSubmit}
      >
        {({ values, errors, touched, setFieldValue, isSubmitting }) => (
          <Form>
            <Grid container spacing={4}>
              {/* Artwork Preview */}
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 3, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Artwork Preview
                  </Typography>
                  <Divider sx={{ mb: 3 }} />
                  
                  <Box sx={{ position: 'relative' }}>
                    <Box
                      component="img"
                      src={artwork.is_revealed ? artwork.image_url : artwork.placeholder_image || '/placeholder.jpg'}
                      alt={artwork.title}
                      sx={{ 
                        width: '100%',
                        height: 'auto',
                        borderRadius: 1,
                        mb: 2,
                        filter: artwork.is_revealed ? 'none' : 'blur(0px) brightness(0.7)'
                      }}
                    />
                    
                    {!artwork.is_revealed && (
                      <Box
                        sx={{
                          position: 'absolute',
                          top: '50%',
                          left: '50%',
                          transform: 'translate(-50%, -50%)',
                          textAlign: 'center',
                          color: 'white',
                          p: 2,
                        }}
                      >
                        <Typography variant="h6">
                          Artwork Hidden
                        </Typography>
                        <Typography variant="body2">
                          This artwork has not been revealed yet
                        </Typography>
                      </Box>
                    )}
                  </Box>
                  
                  <Typography variant="subtitle1" gutterBottom>
                    Status: {artwork.is_revealed ? 'Revealed' : 'Hidden'}
                  </Typography>
                  
                  <Typography variant="subtitle1" gutterBottom>
                    Content Type: {artwork.content_type}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary">
                    Note: Once an artwork is uploaded, you cannot change the actual artwork file or its reveal conditions. You can only edit the title, description, and placeholder image.
                  </Typography>
                </Paper>
                
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Reveal Conditions
                  </Typography>
                  <Divider sx={{ mb: 3 }} />
                  
                  {artwork.reveal_conditions.map((condition, index) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Typography variant="subtitle2">
                        Condition #{index + 1}:
                      </Typography>
                      
                      {condition.condition_type === 'time' && (
                        <Typography variant="body2">
                          Time-based: Reveals on {new Date(condition.condition_value.reveal_at).toLocaleString()}
                        </Typography>
                      )}
                      
                      {condition.condition_type === 'view_count' && (
                        <Typography variant="body2">
                          View Count: Reveals after {condition.condition_value.count} views
                        </Typography>
                      )}
                      
                      {condition.condition_type === 'interactive' && (
                        <Typography variant="body2">
                          Interactive: Reveals after {condition.condition_value.comment_count} comments
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Paper>
              </Grid>
              
              {/* Edit Form */}
              <Grid item xs={12} md={8}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h5" gutterBottom>
                    Edit Artwork Details
                  </Typography>
                  <Divider sx={{ mb: 3 }} />
                  
                  <Stack spacing={3}>
                    <Field
                      as={TextField}
                      name="title"
                      label="Artwork Title"
                      fullWidth
                      variant="outlined"
                      error={touched.title && Boolean(errors.title)}
                      helperText={touched.title && errors.title}
                    />
                    
                    <Field
                      as={TextField}
                      name="description"
                      label="Description"
                      fullWidth
                      variant="outlined"
                      multiline
                      rows={4}
                      error={touched.description && Boolean(errors.description)}
                      helperText={touched.description && errors.description}
                    />
                    
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Custom Placeholder Image (Optional)
                      </Typography>
                      <Typography variant="caption" color="text.secondary" paragraph>
                        This image will be shown before the artwork is revealed. If not changed, the current placeholder will be used.
                      </Typography>
                      
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" gutterBottom>
                          Current placeholder:
                        </Typography>
                        {artwork.placeholder_image ? (
                          <Box
                            component="img"
                            src={artwork.placeholder_image}
                            alt="Current placeholder"
                            sx={{
                              maxWidth: '100%',
                              maxHeight: 150,
                              borderRadius: 1,
                            }}
                          />
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            No custom placeholder set (using default)
                          </Typography>
                        )}
                      </Box>
                      
                      <input
                        accept="image/*"
                        style={{ display: 'none' }}
                        id="placeholder-file"
                        type="file"
                        onChange={(e) => handlePlaceholderChange(e, setFieldValue)}
                      />
                      <label htmlFor="placeholder-file">
                        <Button
                          variant="outlined"
                          component="span"
                          startIcon={<CloudUploadIcon />}
                        >
                          Change Placeholder Image
                        </Button>
                      </label>
                      
                      {touched.placeholder_image && errors.placeholder_image && (
                        <FormHelperText error>
                          {errors.placeholder_image.toString()}
                        </FormHelperText>
                      )}
                      
                      {placeholder && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            New placeholder: {placeholder.name}
                          </Typography>
                          
                          {placeholderPreview && (
                            <Box
                              component="img"
                              src={placeholderPreview}
                              alt="New placeholder preview"
                              sx={{
                                mt: 2,
                                maxWidth: '100%',
                                maxHeight: 150,
                                borderRadius: 1,
                              }}
                            />
                          )}
                        </Box>
                      )}
                    </Box>
                  </Stack>
                  
                  <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between' }}>
                    <Button
                      variant="outlined"
                      onClick={() => navigate(`/artwork/${artworkId}`)}
                    >
                      Cancel
                    </Button>
                    
                    <Button
                      type="submit"
                      variant="contained"
                      color="primary"
                      startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                      disabled={saving || isSubmitting}
                    >
                      {saving ? 'Saving...' : 'Save Changes'}
                    </Button>
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          </Form>
        )}
      </Formik>
    </Container>
  );
};

export default EditArtwork; 