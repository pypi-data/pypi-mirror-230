import { ReactWidget } from "@jupyterlab/apputils";
import React from 'react';
import { APICatalogComponent } from "../components/APICatalogComponent";
import { IProjectProps, IProject } from "../interfaces/CustomInterfaces";


export class APICatalogWidget extends ReactWidget {
  projects: {
    available: IProject[];
    unavailable: IProject[];
  };
  constructor(projects: IProjectProps) {
    super()
    this.projects = projects.projects
    console.log(`Projects in Component => ${JSON.stringify(this.projects, null, 2)}`)
  }

  render(): JSX.Element {
    return <APICatalogComponent projects={this.projects} />
  }
}