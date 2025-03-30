import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { Formik, Form, Field, FieldArray } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';
import { ArtworkCreate, RevealCondition } from '../types';

// Validation schema
const uploadSchema = Yup.object().shape({
  title: Yup.string()
    .required('Title is required')
    .max(255, 'Title must be less than 255 characters'),
  description: Yup.string()
    .max(1000, 'Description must be less than 1000 characters'),
  content_type: Yup.string()
    .required('Content type is required'),
  artwork_file: Yup.mixed()
    .required('Artwork file is required'),
  placeholder_image: Yup.mixed(),
  reveal_conditions: Yup.array().of(
    Yup.object().shape({
      condition_type: Yup.string()
        .required('Condition type is required')
        .oneOf(['time', 'view_count', 'interactive'], 'Invalid condition type'),
      condition_value: Yup.mixed()
        .required('Condition value is required'),
    })
  ).min(1, 'At least one reveal condition is required'),
});

const Upload: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [artwork, setArtwork] = useState<File | null>(null);
  const [artworkPreview, setArtworkPreview] = useState<string | null>(null);
  const [placeholder, setPlaceholder] = useState<File | null>(null);
  const [placeholderPreview, setPlaceholderPreview] = useState<string | null>(null);

  // Redirect if not authenticated or not an artist
  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user?.is_artist)) {
      navigate('/gallery');
    }
  }, [isLoading, isAuthenticated, user, navigate]);

  // Handle file changes
  const handleArtworkChange = (event: React.ChangeEvent<HTMLInputElement>, setFieldValue: any) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setArtwork(file);
      setFieldValue('artwork_file', file);
      
      // Set content type based on file type
      const contentType = file.type;
      setFieldValue('content_type', contentType);
      
      // Generate preview
      const reader = new FileReader();
      reader.onload = () => {
        setArtworkPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

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

  // Initialize a new condition based on type
  const initializeCondition = (type: string): RevealCondition => {
    switch (type) {
      case 'time':
        // Set default reveal date to 1 week from now
        const date = new Date();
        date.setDate(date.getDate() + 7);
        return {
          condition_type: 'time',
          condition_value: {
            reveal_at: date.toISOString().slice(0, 16),
          },
        };
      case 'view_count':
        return {
          condition_type: 'view_count',
          condition_value: {
            count: 100,
          },
        };
      case 'interactive':
        return {
          condition_type: 'interactive',
          condition_value: {
            comment_count: 10,
          },
        };
      default:
        return {
          condition_type: 'time',
          condition_value: {
            reveal_at: new Date().toISOString().slice(0, 16),
          },
        };
    }
  };

  // Handle form submission
  const handleSubmit = async (values: any, { resetForm, setSubmitting }: any) => {
    setUploading(true);
    setUploadSuccess(false);
    setUploadError(null);
    
    try {
      // Prepare artwork data
      const artworkData: ArtworkCreate = {
        title: values.title,
        description: values.description,
        content_type: values.content_type,
        artwork_file: values.artwork_file,
        placeholder_image: values.placeholder_image,
        reveal_conditions: values.reveal_conditions,
      };
      
      // Upload artwork
      await apiService.artworks.create(artworkData);
      
      setUploadSuccess(true);
      resetForm();
      setArtwork(null);
      setArtworkPreview(null);
      setPlaceholder(null);
      setPlaceholderPreview(null);
      
      // Redirect to artist dashboard after a delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 3000);
    } catch (err) {
      setUploadError(
        err instanceof Error ? err.message : 'Failed to upload artwork. Please try again.'
      );
    } finally {
      setUploading(false);
      setSubmitting(false);
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
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Upload New Artwork
      </Typography>
      
      <Typography variant="subtitle1" paragraph align="center" color="text.secondary">
        Upload your invisible artwork and set the conditions for when it will be revealed to viewers.
      </Typography>
      
      <Divider sx={{ my: 4 }} />
      
      {uploadSuccess && (
        <Alert severity="success" sx={{ mb: 4 }}>
          Artwork uploaded successfully! Redirecting to your dashboard...
        </Alert>
      )}
      
      {uploadError && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {uploadError}
        </Alert>
      )}
      
      <Formik
        initialValues={{
          title: '',
          description: '',
          content_type: '',
          artwork_file: null,
          placeholder_image: null,
          reveal_conditions: [
            initializeCondition('time'),
          ],
        }}
        validationSchema={uploadSchema}
        onSubmit={handleSubmit}
      >
        {({ values, errors, touched, setFieldValue, isSubmitting }) => (
          <Form>
            <Grid container spacing={4}>
              {/* Artwork Details */}
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, mb: 3 }}>
                  <Typography variant="h5" gutterBottom>
                    Artwork Details
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
                      <input
                        accept="image/*,video/*,audio/*"
                        style={{ display: 'none' }}
                        id="artwork-file"
                        type="file"
                        onChange={(e) => handleArtworkChange(e, setFieldValue)}
                      />
                      <label htmlFor="artwork-file">
                        <Button
                          variant="contained"
                          component="span"
                          startIcon={<CloudUploadIcon />}
                          fullWidth
                        >
                          Select Artwork File
                        </Button>
                      </label>
                      
                      {touched.artwork_file && errors.artwork_file && (
                        <FormHelperText error>
                          {errors.artwork_file.toString()}
                        </FormHelperText>
                      )}
                      
                      {artwork && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Selected file: {artwork.name} ({(artwork.size / 1024 / 1024).toFixed(2)} MB)
                          </Typography>
                          
                          {artworkPreview && artwork.type.startsWith('image/') && (
                            <Box
                              component="img"
                              src={artworkPreview}
                              alt="Artwork preview"
                              sx={{
                                mt: 2,
                                maxWidth: '100%',
                                maxHeight: 200,
                                borderRadius: 1,
                              }}
                            />
                          )}
                        </Box>
                      )}
                    </Box>
                    
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Custom Placeholder Image (Optional)
                      </Typography>
                      <Typography variant="caption" color="text.secondary" paragraph>
                        This image will be shown before the artwork is revealed. If not provided, a default placeholder will be used.
                      </Typography>
                      
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
                          Select Placeholder Image
                        </Button>
                      </label>
                      
                      {placeholder && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Selected placeholder: {placeholder.name}
                          </Typography>
                          
                          {placeholderPreview && (
                            <Box
                              component="img"
                              src={placeholderPreview}
                              alt="Placeholder preview"
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
                </Paper>
              </Grid>
              
              {/* Reveal Conditions */}
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h5" gutterBottom>
                    Reveal Conditions
                  </Typography>
                  <Typography variant="subtitle2" color="text.secondary" paragraph>
                    Specify when your artwork will be revealed to viewers. You can add multiple conditions.
                  </Typography>
                  <Divider sx={{ mb: 3 }} />
                  
                  <FieldArray name="reveal_conditions">
                    {({ remove, push }) => (
                      <>
                        {values.reveal_conditions.map((condition, index) => (
                          <Box key={index} sx={{ mb: 4, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                              <Typography variant="subtitle1">
                                Condition #{index + 1}
                              </Typography>
                              
                              {values.reveal_conditions.length > 1 && (
                                <Button
                                  size="small"
                                  color="error"
                                  startIcon={<DeleteIcon />}
                                  onClick={() => remove(index)}
                                >
                                  Remove
                                </Button>
                              )}
                            </Stack>
                            
                            <FormControl
                              fullWidth
                              variant="outlined"
                              sx={{ mb: 2 }}
                              error={touched.reveal_conditions?.[index]?.condition_type && 
                                Boolean(errors.reveal_conditions?.[index]?.condition_type)}
                            >
                              <InputLabel>Reveal Type</InputLabel>
                              <Field
                                as={Select}
                                name={`reveal_conditions[${index}].condition_type`}
                                label="Reveal Type"
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                                  const newType = e.target.value;
                                  setFieldValue(`reveal_conditions[${index}].condition_type`, newType);
                                  setFieldValue(
                                    `reveal_conditions[${index}].condition_value`,
                                    initializeCondition(newType).condition_value
                                  );
                                }}
                              >
                                <MenuItem value="time">Time-based</MenuItem>
                                <MenuItem value="view_count">View Count</MenuItem>
                                <MenuItem value="interactive">Interactive</MenuItem>
                              </Field>
                              {touched.reveal_conditions?.[index]?.condition_type && 
                                errors.reveal_conditions?.[index]?.condition_type && (
                                <FormHelperText>
                                  {errors.reveal_conditions?.[index]?.condition_type?.toString()}
                                </FormHelperText>
                              )}
                            </FormControl>
                            
                            {condition.condition_type === 'time' && (
                              <Field
                                as={TextField}
                                name={`reveal_conditions[${index}].condition_value.reveal_at`}
                                label="Reveal Date and Time"
                                type="datetime-local"
                                fullWidth
                                InputLabelProps={{ shrink: true }}
                                error={touched.reveal_conditions?.[index]?.condition_value && 
                                  Boolean(errors.reveal_conditions?.[index]?.condition_value)}
                                helperText={touched.reveal_conditions?.[index]?.condition_value && 
                                  errors.reveal_conditions?.[index]?.condition_value?.toString()}
                              />
                            )}
                            
                            {condition.condition_type === 'view_count' && (
                              <Field
                                as={TextField}
                                name={`reveal_conditions[${index}].condition_value.count`}
                                label="View Count"
                                type="number"
                                fullWidth
                                InputProps={{ inputProps: { min: 1 } }}
                                error={touched.reveal_conditions?.[index]?.condition_value && 
                                  Boolean(errors.reveal_conditions?.[index]?.condition_value)}
                                helperText={touched.reveal_conditions?.[index]?.condition_value && 
                                  errors.reveal_conditions?.[index]?.condition_value?.toString()}
                              />
                            )}
                            
                            {condition.condition_type === 'interactive' && (
                              <Field
                                as={TextField}
                                name={`reveal_conditions[${index}].condition_value.comment_count`}
                                label="Comment Count"
                                type="number"
                                fullWidth
                                InputProps={{ inputProps: { min: 1 } }}
                                error={touched.reveal_conditions?.[index]?.condition_value && 
                                  Boolean(errors.reveal_conditions?.[index]?.condition_value)}
                                helperText={touched.reveal_conditions?.[index]?.condition_value && 
                                  errors.reveal_conditions?.[index]?.condition_value?.toString()}
                              />
                            )}
                          </Box>
                        ))}
                        
                        <Button
                          variant="outlined"
                          startIcon={<AddIcon />}
                          onClick={() => push(initializeCondition('time'))}
                          sx={{ mt: 2 }}
                        >
                          Add Another Condition
                        </Button>
                      </>
                    )}
                  </FieldArray>
                </Paper>
              </Grid>
              
              {/* Submit Button */}
              <Grid item xs={12}>
                <Box sx={{ textAlign: 'center', mt: 2 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={isSubmitting || uploading}
                    startIcon={<CloudUploadIcon />}
                    sx={{ py: 1.5, px: 4 }}
                  >
                    {uploading ? (
                      <>
                        <CircularProgress size={24} sx={{ mr: 1 }} />
                        Uploading...
                      </>
                    ) : 'Upload Artwork'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Form>
        )}
      </Formik>
    </Container>
  );
};

export default Upload; 