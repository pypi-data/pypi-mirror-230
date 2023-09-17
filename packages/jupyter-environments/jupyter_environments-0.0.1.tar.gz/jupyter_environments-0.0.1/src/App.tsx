import { createRoot } from 'react-dom/client';
import Tabs from './Environments';

const div = document.createElement('div');
document.body.appendChild(div);
const root = createRoot(div)

root.render(<Tabs />);
