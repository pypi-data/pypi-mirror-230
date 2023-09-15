import {
    DialogContent,
    DialogTitle,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
    SelectChangeEvent,
    CssBaseline,
    Grid,
    Typography,
    Link,
    TextField
} from '@mui/material';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import { requestAPI } from '../handler';
import {
    ITokensConfigurationProps,
    ITokensConfigurationState
} from '../interfaces/CustomInterfaces';
import { TokensInfoComponent } from './TokenInfo';
import React from 'react';

interface IAllTokensProps {
    endpoints: ITokensConfigurationProps
}

export class TokensConfigurationComponent extends React.Component<
    IAllTokensProps,
    ITokensConfigurationState> {

    constructor(props: IAllTokensProps) {
        super(props);
        this.state = {
            open: true,
            notebook_name: '',
            function_name: '',
            function_url: '',
            tokens: [],
            isFetching: true,
            newTokenName: '',
            endpoints: []
        };

        this._handleChange = this._handleChange.bind(this);
        this._handleSubmit = this._handleSubmit.bind(this);
        this._handleInputChange = this._handleInputChange.bind(this);
    }

    private _onClick = (event: any): void => {
        event.stopPropagation();
        this.setState({
            open: true
        });
    };

    private _onClose = (event: any): void => {
        event.stopPropagation();
        this.setState({
            open: false
        });
    };

    private async _handleChange(event: SelectChangeEvent) {
        event.preventDefault();
        const function_name = (event.target.value as string).split('/')[1]
        const notebook_name = (event.target.value as string).split('/')[0]
        console.log(`Chosen Option => ${event.target.value as string}`);
        const function_url = this.props.endpoints.endpoints.filter(item => item.function_name === function_name && item.notebook_name === notebook_name)
        this.setState({
            ...this.state,
            isFetching: true
        });
        const getAllTokens = await requestAPI<any>('tokens_container', {
            method: 'POST',
            body: JSON.stringify({ function_name, notebook_name })
        });
        console.log(`Tokens List => ${JSON.stringify(getAllTokens.tokens_list, null, 2)}`)
        this.setState({
            ...this.state,
            tokens: getAllTokens.tokens_list,
            isFetching: false,
            function_name: function_name,
            notebook_name: notebook_name,
            function_url: function_url[0].url
        });
        this.forceUpdate()

        console.log(`Response Tokens from React => ${JSON.stringify(getAllTokens.tokens_list, null, 2)}`)
    };

    private async _handleSubmit(event: any): Promise<void> {
        event.preventDefault();
        this.setState({
            ...this.state,
            isFetching: true
        });
        const newTokeninfo = await requestAPI<any>('tokenops', {
            method: 'POST',
            body: JSON.stringify({ token_name: this.state.newTokenName, url: this.state.function_url })
        });
        console.log(`New Token Info => ${JSON.stringify(newTokeninfo.new_token_info)}`);
        const function_name = this.state.function_name
        const notebook_name = this.state.notebook_name

        const getAllTokens = await requestAPI<any>('tokens_container', {
            method: 'POST',
            body: JSON.stringify({ function_name, notebook_name })
        });

        this.setState({
            ...this.state,
            tokens: getAllTokens.tokens_list,
            isFetching: false
        });
        this.forceUpdate()
    }

    private _handleInputChange(event: React.ChangeEvent<HTMLInputElement>): void {
        event.preventDefault();
        this.setState({
            newTokenName: event.target.value as string
        })
    }

    componentDidMount() {
        this.setState({ ...this.state, endpoints: this.props.endpoints.endpoints })
    }

    render(): React.ReactElement {
        let endpoints = this.state.endpoints.length > 0 ? true : false
        return (
            <React.Fragment>
                <CssBaseline />
                <Dialog
                    open={this.state.open}
                    onClick={this._onClick}
                    onClose={this._onClose}
                    maxWidth='md'
                    fullWidth
                    scroll='paper'
                >
                    <DialogTitle>
                        Tokens Configuration
                    </DialogTitle>
                    <DialogContent>
                        <Grid
                            container
                            spacing={2}
                            direction='row'
                            alignItems="center"
                            justifyContent="center">
                            <Grid item xs={12} md={8} lg={6}>
                                <FormControl fullWidth sx={{ mt: 1 }} margin="normal">
                                    <InputLabel htmlFor="select-label">Function name</InputLabel>
                                    <Select
                                        labelId="select-label"
                                        id="simple-select"
                                        value={this.state.notebook_name + "/" + this.state.function_name}
                                        label="Function name"
                                        onChange={(e) => this._handleChange(e)}
                                        autoFocus
                                        inputProps={{
                                            id: "select-label",
                                        }}
                                    >
                                        {endpoints ?
                                            (this.state.endpoints.map((item, index) => {
                                                return <MenuItem key={index} value={item.notebook_name + "/" + item.function_name}>{item.notebook_name + "/" + item.function_name}<br /></MenuItem>
                                            })) :
                                            (<MenuItem key="1" value="">No Function Found<br /></MenuItem>)
                                        }
                                    </Select>
                                </FormControl>
                            </Grid>
                            {this.state.function_name ? (
                                <Grid item>
                                    <form onSubmit={this._handleSubmit}>
                                        <Grid
                                            container
                                            alignItems="center"
                                            justifyContent="center"
                                            direction="row">
                                            <Grid item>
                                                <TextField
                                                    id="name-input"
                                                    name="name"
                                                    label="Name"
                                                    type="text"
                                                    variant='outlined'
                                                    value={this.state.newTokenName}
                                                    onChange={this._handleInputChange}
                                                />
                                            </Grid>
                                            <Grid item sx={{ ml: 1 }}>
                                                <Button variant="contained" color="primary" type="submit">
                                                    Create
                                                </Button>
                                            </Grid>

                                        </Grid>
                                    </form>
                                </Grid>
                            ) : ''}
                        </Grid>

                        {!this.state.isFetching ? (
                            <React.Fragment>
                                <Typography variant="h6" sx={{ m: 2 }}>
                                    Endpoint URL:
                                    <Link href={this.state.function_url} underline="hover">
                                        {this.state.function_url}
                                    </Link>

                                </Typography>
                                <Grid container spacing={2}>
                                    <TokensInfoComponent allTokens={this.state.tokens} url={this.state.function_url!} />
                                </Grid>
                            </React.Fragment>

                        ) : ''}
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={this._onClose} autoFocus sx={{ p: 2 }}>Ok</Button>
                    </DialogActions>
                </Dialog>
            </React.Fragment >
        )
    }
}
