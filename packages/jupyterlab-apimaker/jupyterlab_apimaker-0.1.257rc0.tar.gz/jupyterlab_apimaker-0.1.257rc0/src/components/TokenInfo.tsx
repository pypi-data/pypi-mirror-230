import React from 'react';
import { CssBaseline, Grid, Card, CardHeader, CardContent, CardActions, IconButton } from '@mui/material';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import DeleteIcon from '@mui/icons-material/Delete';
import { ITokensInfoProps } from '../interfaces/CustomInterfaces';
import { requestAPI } from '../handler';

interface IAllTokensInfoProps {
    allTokens: ITokensInfoProps[];
    url: string;
}

interface INewTokenState {
    allTokens: ITokensInfoProps[];
    newTokenName: string;
}

export class TokensInfoComponent extends React.Component<IAllTokensInfoProps, INewTokenState> {

    constructor(props: IAllTokensInfoProps) {
        super(props);
        this.state = {
            allTokens: this.props.allTokens,
            newTokenName: ''
        }
        this._handleRefreshClick = this._handleRefreshClick.bind(this);
        this._handleDeleteClick = this._handleDeleteClick.bind(this);
    }

    private _getHumanDate(currentTimestamp: number | undefined): string {
        if (currentTimestamp) {
            return new Intl.DateTimeFormat('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(currentTimestamp * 1000)
        }
        return '-'
    }

    private async _handleRefreshClick(event: React.MouseEvent<HTMLElement>, item: ITokensInfoProps) {
        event.preventDefault();
        console.log(`Item => ${JSON.stringify(item)}`);
        const updated = await requestAPI<any>('tokenops', {
            method: 'PUT',
            body: JSON.stringify({ item, url: this.props.url })
        });
        console.log(`Updated Token => ${JSON.stringify(updated.token_info, null, 2)}`)
        let token_obj_id = this.state.allTokens.findIndex(obj => obj.rowid === JSON.parse(updated.token_info).rowid);
        let current_tokens = [...this.state.allTokens]
        let single_item = { ...this.state.allTokens[token_obj_id] }
        single_item = JSON.parse(updated.token_info)
        current_tokens[token_obj_id] = single_item
        console.log(`Token Object Id => ${token_obj_id}`)
        console.log(`Single Item => ${JSON.stringify(single_item, null, 2)}`)
        console.log(`Current Token => ${JSON.stringify(current_tokens[token_obj_id], null, 2)}`)
        console.log(`Old Tokens List => ${JSON.stringify(this.state.allTokens, null, 2)}`)
        console.log(`Updated Tokens List => ${JSON.stringify(current_tokens, null, 2)}`)
        this.setState({ ...this.state, allTokens: current_tokens })

        this.forceUpdate()
    }

    private async _handleDeleteClick(event: React.MouseEvent<HTMLElement>, item: ITokensInfoProps) {
        event.preventDefault();
        console.log(`Item => ${JSON.stringify(item)}`);
        const deleteInfo = await requestAPI<any>('tokenops', {
            method: 'DELETE',
            body: JSON.stringify({ item, url: this.props.url })
        });

        this.setState({
            ...this.state,
            allTokens: this.state.allTokens.filter(i => { if (i.rowid != item.rowid) { return i } })
        })

        console.log(`Delete Token Info => ${JSON.stringify(deleteInfo, null, 2)}`)
    }

    render(): React.ReactElement {
        return (
            <React.Fragment>
                <CssBaseline />
                {this.state.allTokens.map((item, index) => {
                    return <Grid item key={index} xs={12} md={8} lg={6}>
                        <Card>
                            <CardHeader
                                title={item.name}>
                            </CardHeader>
                            <CardContent>
                                <p>Id: {item.rowid}</p>
                                <p>Token: {item.token}</p>
                                <p>Status: {item.status}</p>
                                <p>Created: {this._getHumanDate(item.created)}</p>
                                <p>Expires: {this._getHumanDate(item.expires)}</p>
                            </CardContent>
                            <CardActions>
                                <IconButton onClick={(e) => this._handleRefreshClick(e, item)}>
                                    <AutorenewIcon />
                                </IconButton>
                                {
                                    item.name === 'Default' ?
                                        '' :
                                        <IconButton onClick={(e) => this._handleDeleteClick(e, item)}>
                                            <DeleteIcon />
                                        </IconButton>
                                }
                            </CardActions>
                        </Card>
                    </Grid>
                })}
            </React.Fragment >
        )
    }
}