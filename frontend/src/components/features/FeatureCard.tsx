import React from 'react';
import { Card, CardContent, Typography, Button, CardActions } from '@mui/material';

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  onSelect: () => void;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ title, description, icon: Icon, onSelect }) => {
  return (
    <Card sx={{ minWidth: 275, m: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <div style={{ color: '#1976d2', fontSize: 40, marginBottom: 16 }}>{Icon}</div>
        <Typography variant="h5" component="div" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
      </CardContent>
      <CardActions>
        <Button size="small" onClick={onSelect}>Select</Button>
      </CardActions>
    </Card>
  );
};

export default FeatureCard;
