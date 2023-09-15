import React from 'react';
import { Box, Container, Typography } from '@mui/material';

const Footer: React.FC = (): JSX.Element => {
  return (
    <React.Fragment>
      <Container maxWidth='lg'>
        <Box sx={{
          display: "flex",
          position: "fixed",
          bottom: "15px",
          right: "20px",
          paddingRight: "20px",
          paddingBottom: "15px",
          width: "100%",
          justifyContent: "flex-end"
        }}>
          <Typography variant='body2'>
            Made with &#10084;&#65039; by Navteca.
          </Typography>
        </Box>
      </Container>
    </React.Fragment >
  )
}

export default Footer