import React from 'react';
import { CardActions, Card, CardContent, Typography, CssBaseline, Stack } from '@mui/material';
import { IProject } from '../interfaces/CustomInterfaces';
import UserFunctionDialog from './UserFunctionDialog';

interface IProjectProps {
  project: IProject
}

const APICardComponent: React.FC<IProjectProps> = (props): JSX.Element => {
  return (
    <React.Fragment>
      <CssBaseline />
      <Card variant='outlined'>
        <CardContent>
          <Stack direction='row' justifyContent="space-between"
            alignItems="center">
            <Typography sx={{ fontSize: 14 }} color="text.secondary" noWrap gutterBottom>
              {props.project.function_name}
            </Typography>
          </Stack>
          <Typography variant="h6" noWrap>
            {`Image Tag: ${props.project.image_tag}`}
          </Typography>
          <Typography noWrap paragraph>
            {`Description: ${props.project.help_message ? props.project.help_message : 'No description provided.'}`}
          </Typography>
        </CardContent>
        <CardActions>
          <UserFunctionDialog project={props.project} />
        </CardActions>
      </Card>
    </React.Fragment>
  )
};

export default APICardComponent