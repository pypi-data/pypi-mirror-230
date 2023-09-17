import { useState, useEffect } from 'react';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { ThemeProvider, BaseStyles, Box } from '@primer/react';
import { UnderlineNav } from '@primer/react/drafts';
import { RecyclingIcon } from '@datalayer/icons-react';
import AboutTab from './components/AboutTab';
import MainTab from './components/MainTab';
import { requestAPI } from './handler';

export type JupyterFrontEndProps = {
  app?: JupyterFrontEnd;
}

const Environments = (props: JupyterFrontEndProps) => {
  const { app } = props;
  const [tab, setTab] = useState(1);
  const [version, setVersion] = useState('');
  useEffect(() => {
    requestAPI<any>('config')
    .then(data => {
      setVersion(data.version);
    })
    .catch(reason => {
      console.error(
        `Error while accessing the jupyter server nbmodel extension.\n${reason}`
      );
    });
  });
  return (
    <>
      <ThemeProvider>
        <BaseStyles>
          <Box>
            <Box>
              <UnderlineNav aria-label="nbmodel">
                <UnderlineNav.Item aria-label="nbmodel-nbmodel" aria-current={tab === 1 ? "page" : undefined} icon={() => <RecyclingIcon colored/>} onSelect={e => {e.preventDefault(); setTab(1);}}>
                  Environments
                </UnderlineNav.Item>
                <UnderlineNav.Item aria-label="nbmodel-about" aria-current={tab === 2 ? "page" : undefined} icon={() => <RecyclingIcon colored/>} onSelect={e => {e.preventDefault(); setTab(2);}}>
                  About
                </UnderlineNav.Item>
              </UnderlineNav>
            </Box>
            <Box m={3}>
              {tab === 1 && app && <MainTab app={app} />}
              {tab === 2 && <AboutTab version={version} />}
            </Box>
          </Box>
        </BaseStyles>
      </ThemeProvider>
    </>
  );
}

export default Environments;
