import { ReactWidget } from '@jupyterlab/apputils';
import Environments from './Environments';

export class EnvironmentsWidget extends ReactWidget {
  constructor() {
    super();
    this.addClass('dla-Container');
  }

  render(): JSX.Element {
    return <Environments />
  }
}
