import React from 'react';
import { Clipboard } from '@jupyterlab/apputils';
import { IconButton, Button, Typography, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Stack, Box, Divider } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { IProject } from '../interfaces/CustomInterfaces';
import isUndefined from 'lodash.isundefined';

interface IProjectProps {
  project: IProject
}

const UserFunctionDialog: React.FC<IProjectProps> = (props): JSX.Element => {
  const [open, setOpen] = React.useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  }

  const handleClose = () => {
    setOpen(false);
  }

  const getCode = `import requests\nr = requests.get('${props.project.endpoint_url}')\nr.content`
  const postCode = `import requests\nr = requests.post('${props.project.endpoint_url}', json={<function_params>})\nr.content`

  const prepareJSONForExample = (function_params: string | undefined): string => {
    let postCodeFixed: string = ''
    if (isUndefined(function_params)) {
      const re = /<function_params>/gi;
      postCodeFixed = postCode.replace(re, '');
      return postCodeFixed
    }

    let params = []
    for (let p of function_params.split(',')) {
      params.push(`"${p.trim()}": <value>`)
    }
    const re = /<function_params>/gi;
    postCodeFixed = postCode.replace(re, params.join(', '));
    return postCodeFixed
  }

  return (
    <React.Fragment>
      <Button size="small" onClick={handleClickOpen}>Learn More</Button>
      <Dialog
        open={open}
        keepMounted
        onClose={handleClose}
        aria-labelledby='user-function-dialog-title'
        aria-describedby='user-function-dialog-description'>
        <DialogTitle id='user-function-dialog-title'>
          <Typography variant='h5' gutterBottom>
            {'Endpoint Information'}
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ paddingBottom: '8px' }}>
          <DialogContentText id='user-function-dialog-description'>
            <Typography>
              {`Description: ${props.project.help_message ? props.project.help_message : 'No description has been provided.'}\n`}
            </Typography>
            <Typography>
              {`Parameters: ${props.project.function_params ? props.project.function_params : 'This functions doesn\'t require parameters.'}`}
            </Typography>
            <Divider />
            <Stack justifyContent="flex-start"
              alignItems="stretch" spacing={0} sx={{ paddingTop: '8px' }}>
              <Typography variant='h6'>
                {'GET Method'}
              </Typography>
              <Box sx={{
                backgroundColor: '#f5f5f5',
                border: '1px solid #cccccc',
                padding: '8px 40px 8px 8px',
                position: 'relative'
              }}>
                <Typography noWrap paragraph gutterBottom sx={{
                  display: 'block',
                  fontFamily: 'monospace',
                  fontSize: '13px',
                  tabSize: 2,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-all',
                  wordWrap: 'break-word'
                }}>
                  {getCode}
                </Typography>
                <IconButton aria-label='copy' onClick={() => Clipboard.copyToSystem(getCode)} sx={{
                  bottom: '0px',
                  position: 'absolute',
                  right: '8px'
                }}>
                  <ContentCopyIcon color="action" fontSize='small' />
                </IconButton>
              </Box>
              <Typography variant='h6' sx={{ paddingTop: '8px' }}>
                {'POST Method'}
              </Typography>
              <Box sx={{
                backgroundColor: '#f5f5f5',
                border: '1px solid #cccccc',
                padding: '8px 40px 8px 8px',
                position: 'relative'
              }}>
                <Typography noWrap paragraph gutterBottom sx={{
                  display: 'block',
                  fontFamily: 'monospace',
                  fontSize: '13px',
                  tabSize: 2,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-all',
                  wordWrap: 'break-word'
                }}>
                  {prepareJSONForExample(props.project.function_params ? props.project.function_params : undefined)}
                </Typography>
                <IconButton aria-label='copy' onClick={() => Clipboard.copyToSystem(prepareJSONForExample(props.project.function_params ? props.project.function_params : undefined))} sx={{
                  bottom: '0px',
                  position: 'absolute',
                  right: '8px'
                }}>
                  <ContentCopyIcon color="action" fontSize='small' />
                </IconButton>
              </Box>
            </Stack>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment >
  )
};

export default UserFunctionDialog