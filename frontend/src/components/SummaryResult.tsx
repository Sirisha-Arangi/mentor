import { Paper, Typography, Box, IconButton, Tooltip } from '@mui/material';
import { ContentCopy } from '@mui/icons-material';
import { useState } from 'react';

interface SummaryResultProps {
  content: string;
}

const SummaryResult = ({ content }: SummaryResultProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <Paper sx={{ p: 3, mt: 3, position: 'relative' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Generated Summary</Typography>
        <Tooltip title={copied ? "Copied!" : "Copy to clipboard"}>
          <IconButton onClick={handleCopy} size="small">
            <ContentCopy fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      <Typography 
        component="div" 
        sx={{ 
          whiteSpace: 'pre-wrap',
          lineHeight: 1.6,
          '& p': {
            marginBottom: '1em'
          }
        }}
        dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, '<br />') }}
      />
    </Paper>
  );
};

export default SummaryResult;
