import React from "react";
import { Link } from 'react-router-dom';
import { Box, Button, Container, Typography } from '@mui/material';

const NotFound: React.FC = () => {
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          py: 8,
          minHeight: 'calc(100vh - 200px)',
        }}
      >
        <Typography variant="h1" sx={{ mb: 4 }}>
          404
        </Typography>
        
        <Typography variant="h4" sx={{ mb: 2 }}>
          Artwork Not Found
        </Typography>
        
        <Typography variant="body1" sx={{ mb: 4 }}>
          The artwork you're looking for might be hidden, still being created, or it simply doesn't exist.
          Maybe it's waiting for the right moment to reveal itself?
        </Typography>
        
        <Button component={Link} to="/" variant="contained" size="large">
          Return to Gallery
        </Button>
      </Box>
    </Container>
  );
};

export default NotFound; 