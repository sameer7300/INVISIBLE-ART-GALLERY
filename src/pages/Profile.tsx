import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Divider,
  Grid,
  Tab,
  Tabs,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  Paper,
} from '@mui/material';
import { Person as PersonIcon, VpnKey as VpnKeyIcon, Save as SaveIcon } from '@mui/icons-material';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';

// Define interface for Tab Panel props
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// Tab Panel component
const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

// Profile Info Schema
const profileSchema = Yup.object({
  username: Yup.string()
    .min(3, 'Username should be of minimum 3 characters length')
    .max(20, 'Username should be of maximum 20 characters length')
    .required('Username is required'),
  first_name: Yup.string()
    .max(50, 'First name should be of maximum 50 characters length'),
  last_name: Yup.string()
    .max(50, 'Last name should be of maximum 50 characters length'),
  bio: Yup.string()
    .max(500, 'Bio should be of maximum 500 characters length'),
});

// Password Schema
const passwordSchema = Yup.object({
  old_password: Yup.string()
    .required('Current password is required'),
  new_password: Yup.string()
    .min(8, 'Password should be of minimum 8 characters length')
    .required('New password is required'),
  new_password_confirm: Yup.string()
    .oneOf([Yup.ref('new_password')], 'Passwords must match')
    .required('Confirm your new password'),
});

const Profile: React.FC = () => {
  const { user, updateUser, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [profileUpdateSuccess, setProfileUpdateSuccess] = useState(false);
  const [profileUpdateError, setProfileUpdateError] = useState<string | null>(null);
  const [passwordUpdateSuccess, setPasswordUpdateSuccess] = useState(false);
  const [passwordUpdateError, setPasswordUpdateError] = useState<string | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isLoading, isAuthenticated, navigate]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleProfileUpdate = async (values: any, { setSubmitting }: any) => {
    try {
      setProfileUpdateSuccess(false);
      setProfileUpdateError(null);
      
      const updatedUser = await apiService.auth.updateProfile(values);
      updateUser(updatedUser);
      
      setProfileUpdateSuccess(true);
    } catch (err) {
      setProfileUpdateError(
        err instanceof Error ? err.message : 'Failed to update profile. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handlePasswordUpdate = async (values: any, { setSubmitting, resetForm }: any) => {
    try {
      setPasswordUpdateSuccess(false);
      setPasswordUpdateError(null);
      
      await apiService.auth.changePassword(values.old_password, values.new_password);
      
      setPasswordUpdateSuccess(true);
      resetForm();
    } catch (err) {
      setPasswordUpdateError(
        err instanceof Error ? err.message : 'Failed to update password. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading || !user) {
    return (
      <Container sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <Grid container spacing={4}>
        {/* User Summary Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 4 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar
                src={user.profile_picture || `https://ui-avatars.com/api/?name=${user.username}&size=200&background=random`}
                alt={user.username}
                sx={{ width: 120, height: 120, mx: 'auto', mb: 2 }}
              />
              <Typography variant="h5" gutterBottom>
                {user.first_name && user.last_name
                  ? `${user.first_name} ${user.last_name}`
                  : user.username}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                @{user.username}
              </Typography>
              {user.is_artist && (
                <Typography
                  variant="caption"
                  sx={{
                    display: 'inline-block',
                    py: 0.5,
                    px: 1,
                    borderRadius: 1,
                    bgcolor: 'primary.main',
                    color: 'white',
                    mb: 2,
                  }}
                >
                  Artist
                </Typography>
              )}
              <Typography variant="body1" sx={{ mt: 2 }}>
                {user.bio || 'No bio added yet.'}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Member since: {new Date(user.created_at).toLocaleDateString()}
              </Typography>
            </CardContent>
          </Card>

          {user.is_artist && (
            <Button
              variant="contained"
              fullWidth
              onClick={() => navigate('/dashboard')}
              sx={{ mb: 2 }}
            >
              Go to Artist Dashboard
            </Button>
          )}
        </Grid>

        {/* Profile Edit Tabs */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 0 }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="profile tabs"
              variant="fullWidth"
            >
              <Tab icon={<PersonIcon />} label="Profile Info" />
              <Tab icon={<VpnKeyIcon />} label="Password" />
            </Tabs>

            {/* Profile Info Panel */}
            <TabPanel value={tabValue} index={0}>
              {profileUpdateSuccess && (
                <Alert severity="success" sx={{ mb: 3 }}>
                  Profile updated successfully!
                </Alert>
              )}
              {profileUpdateError && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {profileUpdateError}
                </Alert>
              )}

              <Formik
                initialValues={{
                  username: user.username,
                  first_name: user.first_name || '',
                  last_name: user.last_name || '',
                  bio: user.bio || '',
                }}
                validationSchema={profileSchema}
                onSubmit={handleProfileUpdate}
              >
                {({ errors, touched, isSubmitting }) => (
                  <Form>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <Field
                          as={TextField}
                          fullWidth
                          name="username"
                          label="Username"
                          variant="outlined"
                          error={touched.username && Boolean(errors.username)}
                          helperText={touched.username && errors.username}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Field
                          as={TextField}
                          fullWidth
                          name="first_name"
                          label="First Name"
                          variant="outlined"
                          error={touched.first_name && Boolean(errors.first_name)}
                          helperText={touched.first_name && errors.first_name}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Field
                          as={TextField}
                          fullWidth
                          name="last_name"
                          label="Last Name"
                          variant="outlined"
                          error={touched.last_name && Boolean(errors.last_name)}
                          helperText={touched.last_name && errors.last_name}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Field
                          as={TextField}
                          fullWidth
                          name="bio"
                          label="Bio"
                          variant="outlined"
                          multiline
                          rows={4}
                          error={touched.bio && Boolean(errors.bio)}
                          helperText={touched.bio && errors.bio}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Button
                          type="submit"
                          variant="contained"
                          startIcon={<SaveIcon />}
                          disabled={isSubmitting}
                          sx={{ mt: 2 }}
                        >
                          {isSubmitting ? 'Saving...' : 'Save Changes'}
                        </Button>
                      </Grid>
                    </Grid>
                  </Form>
                )}
              </Formik>
            </TabPanel>

            {/* Password Panel */}
            <TabPanel value={tabValue} index={1}>
              {passwordUpdateSuccess && (
                <Alert severity="success" sx={{ mb: 3 }}>
                  Password updated successfully!
                </Alert>
              )}
              {passwordUpdateError && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {passwordUpdateError}
                </Alert>
              )}

              <Formik
                initialValues={{
                  old_password: '',
                  new_password: '',
                  new_password_confirm: '',
                }}
                validationSchema={passwordSchema}
                onSubmit={handlePasswordUpdate}
              >
                {({ errors, touched, isSubmitting }) => (
                  <Form>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <Field
                          as={TextField}
                          fullWidth
                          type="password"
                          name="old_password"
                          label="Current Password"
                          variant="outlined"
                          error={touched.old_password && Boolean(errors.old_password)}
                          helperText={touched.old_password && errors.old_password}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Field
                          as={TextField}
                          fullWidth
                          type="password"
                          name="new_password"
                          label="New Password"
                          variant="outlined"
                          error={touched.new_password && Boolean(errors.new_password)}
                          helperText={touched.new_password && errors.new_password}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Field
                          as={TextField}
                          fullWidth
                          type="password"
                          name="new_password_confirm"
                          label="Confirm New Password"
                          variant="outlined"
                          error={touched.new_password_confirm && Boolean(errors.new_password_confirm)}
                          helperText={touched.new_password_confirm && errors.new_password_confirm}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Button
                          type="submit"
                          variant="contained"
                          color="secondary"
                          startIcon={<VpnKeyIcon />}
                          disabled={isSubmitting}
                          sx={{ mt: 2 }}
                        >
                          {isSubmitting ? 'Updating...' : 'Update Password'}
                        </Button>
                      </Grid>
                    </Grid>
                  </Form>
                )}
              </Formik>
            </TabPanel>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Profile; 