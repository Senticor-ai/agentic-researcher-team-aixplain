import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar, Alignment } from '@blueprintjs/core';
import Dashboard from './pages/Dashboard';
import TeamDetail from './pages/TeamDetail';
import '@blueprintjs/core/lib/css/blueprint.css';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar className="app-navbar">
          <Navbar.Group align={Alignment.LEFT}>
            <Navbar.Heading>
              <strong>Senticor Agent Team Monitor</strong>
            </Navbar.Heading>
          </Navbar.Group>
        </Navbar>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/teams/:teamId" element={<TeamDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
