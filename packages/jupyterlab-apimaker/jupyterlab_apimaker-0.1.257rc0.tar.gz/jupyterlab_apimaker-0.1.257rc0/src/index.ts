import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from "@jupyterlab/application";
import {
    InputDialog,
    ToolbarButton,
    MainAreaWidget,
    Clipboard
} from "@jupyterlab/apputils";
import { PageConfig } from "@jupyterlab/coreutils";
import { DocumentRegistry } from "@jupyterlab/docregistry";
import { ILauncher } from "@jupyterlab/launcher";
import { IMainMenu } from "@jupyterlab/mainmenu";
import { NotebookPanel, INotebookModel } from "@jupyterlab/notebook";
import { reactIcon } from "@jupyterlab/ui-components";

import { DisposableDelegate, IDisposable } from "@lumino/disposable";
import { Menu, Widget } from "@lumino/widgets";

import { INotification } from "jupyterlab_toastify";

import isEmpty from "lodash.isempty";
import isEqual from "lodash.isequal";
import isUndefined from "lodash.isundefined";

import { requestAPI } from "./handler";
import { INotebookInfo } from "./interfaces/CustomInterfaces";
import { APICatalogWidget } from "./widgets/APICatalogWidget";
import { TokensConfigurationWidget } from "./widgets/TokensConfigurationWidget";

const plugin: JupyterFrontEndPlugin<void> = {
    id: "jupyterlab_apimaker:plugin",
    autoStart: true,
    optional: [ILauncher, IMainMenu],
    activate,
};

let openedFilename: string;
let pathToNotebook: string;

async function sendNotebookText(
    panel: NotebookPanel
): Promise<INotebookInfo | undefined> {
    openedFilename = panel.title.label.split(".")[0].replace(
        /[ ._]/g,
        "-"
    );
    console.log(`Panel Name => ${panel.title.label}`)
    console.log(`Panel Name Fix => ${openedFilename}`)
    console.log(`Panel Model => ${panel.model?.toJSON()}`)
    console.log(`Panel PageConfig and Model Path => ${PageConfig.getOption('serverRoot')} - ${panel.context.contentsModel?.path}`)
    pathToNotebook = `${PageConfig.getOption('serverRoot')}/${panel.context.contentsModel?.path}`
    const createProjectResult = await requestAPI<any>("process_notebook", {
        method: "POST",
        body: JSON.stringify(panel.model?.toJSON()),
    });

    if (createProjectResult.functions) {
        return createProjectResult;
    }

    return undefined;
}

async function showFunctions(
    functionsInNotebook: INotebookInfo
): Promise<string | void> {
    let functionsToSelect = functionsInNotebook.functions.map(
        (el: { [key: string]: string }) => el.function_name
    );
    const functionSelector = await InputDialog.getItem({
        title: "Create New API",
        label: "Select Function:",
        items: functionsToSelect,
        okLabel: "Next",
        cancelLabel: "Cancel",
    });

    if (!functionSelector.button.accept) {
        return;
    }

    if (isUndefined(functionSelector.value)) {
        return undefined;
    }

    return functionSelector.value!;
}

export class ButtonExtension
    implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>
{
    createNew(
        panel: NotebookPanel,
        _: DocumentRegistry.IContext<INotebookModel>
    ): IDisposable {
        const printNotebookText = async () => {
            //         notebookTracker.currentWidget?.update()
            // notebookTracker.currentWidget?.title.label
            const functionsInNotebook = await sendNotebookText(panel);
            if (isUndefined(functionsInNotebook)) {
                INotification.warning(
                    "There are no functions in this notebook. Please, add one at least.",
                    { autoClose: 3000 }
                );
                return;
            }

            const selectedFunction = await showFunctions(functionsInNotebook);

            if (isUndefined(selectedFunction)) {
                return;
            }

            const functionToMakeAPIFrom = functionsInNotebook.functions.filter(
                (el: { [key: string]: string }) => el.function_name == selectedFunction
            );

            if (isEmpty(functionToMakeAPIFrom)) {
                INotification.warning(
                    `There is not a function with the name ${selectedFunction}.`,
                    { autoClose: 3000 }
                );
                return;
            }

            const requestDomain = await InputDialog.getText({
                title: "Create New API",
                label: "Provide the domain of the API:",
                okLabel: "Next",
                cancelLabel: "Cancel",
            });

            if (!requestDomain.button.accept) {
                return;
            }

            if (isEmpty(requestDomain.value)) {
                INotification.warning(`Please, insert a domain.`, { autoClose: 3000 });
                return;
            }

            const requestedDomain = requestDomain.value
                ?.replace(" ", "_")
                .replace(/[^a-zA-Z0-9]/g, "_");

            const requestAPIVersion = await InputDialog.getText({
                title: "Create New API",
                label: "Provide the version of the API:",
                okLabel: "Create",
                cancelLabel: "Cancel",
            });

            if (!requestAPIVersion.button.accept) {
                return;
            }

            if (isEmpty(requestAPIVersion.value)) {
                INotification.warning(`Please, insert a version.`, { autoClose: 3000 });
                return;
            }

            const requestedAPIVersion = requestAPIVersion.value?.replace(
                /[ ._]/g,
                "-"
            );
            console.log(`Version => ${requestedAPIVersion}`);

            let id = await INotification.inProgress("Baking API...");

            const sendFunctionToMakeAPIFrom = await requestAPI<any>("make_api", {
                method: "POST",
                body: JSON.stringify({
                    userCode: functionToMakeAPIFrom[0],
                    notebookName: openedFilename,
                    domain: requestedDomain,
                    apiVersion: requestedAPIVersion,
                    pathToNotebook: pathToNotebook
                }),
            });

            if (!isEqual(sendFunctionToMakeAPIFrom.statusCode, 200)) {
                INotification.update({
                    toastId: id,
                    message: `There has been an error creating the endpoint, please contact the administrator os API Maker.`,
                    type: "warning",
                });
                return;
            }

            let messages = [
                `Let's wait for the service to be ready. This may take a while.`,
                `We're still working on it. Thank you for your patience`,
                `This process usually take some time. Please be patient.`,
                `We will let you know when your serivce is ready.`,
                `Thank you for your patience, we're still working on it.`
            ];
            const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

            const updateNotification = (toastId: unknown, message: string) => {
                INotification.update({
                    toastId: <React.ReactText> toastId,
                    message
                });
            }

            for (let i = 1; i <= 15; i++) {
                let timer = i * Math.floor(Math.random() * (30000 - 15000 + 1)) + 15000
                let message = messages[Math.floor(Math.random() * messages.length)]
                await delay(timer)
                updateNotification(id, message)
            }

            INotification.update({
                toastId: id,
                message: `Your service is ready: ${sendFunctionToMakeAPIFrom.body.url}`,
                type: "success",
                buttons: [
                    {
                        label: 'Copy',
                        callback: () => Clipboard.copyToSystem(sendFunctionToMakeAPIFrom.body.url)
                    }
                ],
            });

            console.log(
                `URL and Token => ${JSON.stringify(
                    sendFunctionToMakeAPIFrom.body.defaultToken,
                    null,
                    2
                )}`
            );
        };

        const button = new ToolbarButton({
            className: "apimaker",
            label: "Bake API",
            onClick: printNotebookText,
            tooltip: "Create an API based on a selected function.",
        });

        panel.toolbar.insertItem(10, "make-api", button);
        return new DisposableDelegate(() => {
            button.dispose();
        });
    }
}

function activate(
    app: JupyterFrontEnd,
    launcher: ILauncher,
    mainMenu: IMainMenu,
    panel: NotebookPanel
): void {
    console.log("API Baker Extension Activated");
    const { commands } = app;
    commands.addCommand("create-react-widget", {
        caption: "Show API Collection",
        label: "API Collection",
        icon: (args) => (args["isPalette"] ? undefined : reactIcon),
        execute: async () => {
            const getProjects = await requestAPI<any>("api_catalog", {
                method: "GET",
            });
            if (isEqual(getProjects.statusCode, 200)) {
                console.log(`Projects => ${JSON.stringify(getProjects, null, 2)}`);
            }
            const content = new APICatalogWidget(getProjects);
            const widget = new MainAreaWidget<APICatalogWidget>({ content });
            widget.title.label = "API Collection";
            widget.title.icon = reactIcon;
            app.shell.add(widget, "main");
        },
    });

    const command = "jlab-apibaker:command";
    commands.addCommand(command, {
        label: "Tokens Configuration",
        caption: "Tokens Configuration",
        execute: async () => {
            const getAllEndpoints = await requestAPI<any>("tokens", {
                method: "GET",
            });
            const content = new TokensConfigurationWidget({
                endpoints: getAllEndpoints.all_endpoints,
                jwt: getAllEndpoints.jwt,
            });

            Widget.attach(content, document.body);
        },
    });

    const menu = new Menu({ commands: app.commands });
    menu.title.label = "API Baker";
    menu.addItem({ command });

    mainMenu.addMenu(menu, { rank: 900 });

    Promise.all([app.restored]).then(() => {
        if (app.shell.currentWidget) {
            app.shell.currentWidget.update();
            if (
                isEqual(app.shell.currentWidget.title.label.split(".").pop(), "ipynb")
            ) {
                openedFilename = app.shell.currentWidget.title.label.split(".")[0];
                pathToNotebook = `${PageConfig.getOption('serverRoot')}/${panel.context.contentsModel?.path}`
            }
        }
    });

    if (launcher) {
        launcher.add({
            command: "create-react-widget",
        });
    }
    app.docRegistry.addWidgetExtension("Notebook", new ButtonExtension());
}

export default plugin;
