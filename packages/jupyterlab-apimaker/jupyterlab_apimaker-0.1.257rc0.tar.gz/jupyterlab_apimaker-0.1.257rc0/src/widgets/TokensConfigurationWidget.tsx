import { ReactWidget } from "@jupyterlab/apputils";
import React from 'react';
import { TokensConfigurationComponent } from '../components/TokensConfiguration';
import { ITokensConfigurationProps } from "../interfaces/CustomInterfaces";


export class TokensConfigurationWidget extends ReactWidget {
    tokenDummyData: ITokensConfigurationProps;

    constructor(master_db_info: ITokensConfigurationProps) {
        super()
        this.tokenDummyData = master_db_info;

    }

    render(): JSX.Element {
        return <TokensConfigurationComponent endpoints={this.tokenDummyData} />
    }
}

