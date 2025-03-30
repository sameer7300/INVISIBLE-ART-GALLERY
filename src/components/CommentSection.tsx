import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Avatar,
  Divider,
  Paper,
  Stack,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { Comment, CommentCreate } from '../types';
import apiService from '../services/api';

interface CommentSectionProps {
  artworkId: number;
  comments: Comment[];
  onCommentAdded?: (newComment: Comment) => void;
}

const CommentSection: React.FC<CommentSectionProps> = ({
  artworkId,
  comments,
  onCommentAdded,
}) => {
  const { user, isAuthenticated } = useAuth();
  const [commentText, setCommentText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [commentAdded, setCommentAdded] = useState(false);

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  // Generate user avatar with initials if no avatar image
  const generateInitialsAvatar = (username: string) => {
    return username.substring(0, 2).toUpperCase();
  };

  // Handle form submission
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!commentText.trim()) return;
    
    setIsSubmitting(true);
    setError(null);
    setCommentAdded(false);
    
    try {
      const commentData: CommentCreate = {
        artwork_id: artworkId,
        content: commentText.trim(),
      };
      
      const newComment = await apiService.artworks.addComment(artworkId, commentData);
      
      setCommentText('');
      setCommentAdded(true);
      
      // Notify parent component if callback provided
      if (onCommentAdded) {
        onCommentAdded(newComment);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to add comment. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Comments ({comments.length})
      </Typography>
      
      <Divider sx={{ mb: 3 }} />
      
      {/* Comment Form */}
      {isAuthenticated ? (
        <Paper sx={{ p: 2, mb: 4 }}>
          <form onSubmit={handleSubmit}>
            <Stack spacing={2}>
              {commentAdded && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  Your comment has been added!
                </Alert>
              )}
              
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              
              <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                <Avatar 
                  src={user?.avatar}
                  sx={{ mr: 2 }}
                >
                  {!user?.avatar && user ? generateInitialsAvatar(user.username) : null}
                </Avatar>
                
                <TextField
                  variant="outlined"
                  fullWidth
                  multiline
                  rows={3}
                  placeholder="Add a comment..."
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  disabled={isSubmitting}
                />
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  endIcon={isSubmitting ? <CircularProgress size={20} /> : <SendIcon />}
                  disabled={isSubmitting || !commentText.trim()}
                >
                  {isSubmitting ? 'Posting...' : 'Post Comment'}
                </Button>
              </Box>
            </Stack>
          </form>
        </Paper>
      ) : (
        <Paper sx={{ p: 3, mb: 4, textAlign: 'center', bgcolor: 'background.default' }}>
          <Typography variant="body1" gutterBottom>
            Please log in to add comments.
          </Typography>
          <Button 
            variant="contained" 
            color="primary"
            href="/login"
            sx={{ mt: 1 }}
          >
            Login
          </Button>
        </Paper>
      )}
      
      {/* Comment List */}
      {comments.length > 0 ? (
        <Stack spacing={3}>
          {comments.map((comment) => (
            <Paper key={comment.id} sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', mb: 1 }}>
                <Avatar 
                  src={comment.user.avatar}
                  sx={{ mr: 2, width: 40, height: 40 }}
                >
                  {!comment.user.avatar ? generateInitialsAvatar(comment.user.username) : null}
                </Avatar>
                
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {comment.user.username}
                      {comment.user.is_artist && (
                        <Typography 
                          component="span" 
                          sx={{ 
                            ml: 1, 
                            fontSize: '0.75rem', 
                            bgcolor: 'secondary.main', 
                            color: 'white',
                            px: 1,
                            py: 0.5,
                            borderRadius: 1,
                          }}
                        >
                          Artist
                        </Typography>
                      )}
                    </Typography>
                    
                    <Typography variant="caption" color="text.secondary">
                      {formatDate(comment.created_at)}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body1" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
                    {comment.content}
                  </Typography>
                </Box>
              </Box>
            </Paper>
          ))}
        </Stack>
      ) : (
        <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'background.default' }}>
          <Typography variant="body1">
            No comments yet. Be the first to share your thoughts!
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default CommentSection; 