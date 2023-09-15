export interface IProject {
  username?: string;
  function_name?: string;
  function_params?: string;
  image_tag?: string;
  endpoint_url?: string;
  port?: number;
  help_message?: string;
  parameters?: string;
  active?: number;
};

export interface IProjectProps {
  projects: {
    available: IProject[];
    unavailable: IProject[];
  };
};

export interface INotebookInfo {
  python_version: string;
  functions: [{ [key: string]: string }];
};

export interface ITokensInfoProps {
  rowid: number;
  name: string;
  token: string;
  status: string;
  created: number;
  expires: number | undefined;
};

export interface IEndpointsInfoProps {
  rowid: string;
  function_name: string;
  notebook_name: string;
  url: string;
}

export interface ITokensConfigurationProps {
  endpoints: IEndpointsInfoProps[];
  jwt: string;
}

export interface ITokensConfigurationState {
  open: boolean;
  notebook_name?: string;
  function_name?: string;
  function_url?: string;
  tokens: ITokensInfoProps[] | [];
  isFetching: boolean;
  newTokenName: string;
  endpoints: IEndpointsInfoProps[];
};