import React from 'react';
import { Grid, Typography, CssBaseline, Box } from '@mui/material';
import APICardComponent from "./APICard";
import Footer from './Footer';
import { IProjectProps } from '../interfaces/CustomInterfaces';


export class APICatalogComponent extends React.Component<IProjectProps> {
    constructor(props: IProjectProps) {
        super(props)
    }

    render(): React.ReactElement {
        return (
            <React.Fragment>
                <CssBaseline />
                <Grid container spacing={2} sx={{
                    paddingLeft: '20px',
                    paddingRight: '20px',
                    paddingTop: '20px',
                    overflow: 'auto',
                    maxHeight: '100%'
                }}>
                    <Grid item xs={12}>
                        <Box sx={{ my: 4 }}>
                            <Typography variant='h1' component='div' align='center' gutterBottom>
                                API Collection
                            </Typography>
                        </Box>
                    </Grid>
                    {(this.props.projects.available.length == 0 && this.props.projects.unavailable.length == 0) ? (
                        <Grid item xs={12}>
                            <Box sx={{ my: 4 }}>
                                <Typography variant='h3' component='div' align='center' gutterBottom>
                                    No API found yet.
                                </Typography>
                            </Box>
                        </Grid>
                    ) : (null)}
                    {this.props.projects.available.map((item) => (
                        <Grid item xs={12} md={6} xl={2}>
                            <APICardComponent project={item} />
                        </Grid>
                    ))}
                    {this.props.projects.unavailable.map((item) => (
                        <Grid item xs={12} md={6} xl={2}>
                            <APICardComponent project={item} />
                        </Grid>
                    ))}
                </Grid>
                <Footer />
            </React.Fragment>
        )
    }
}