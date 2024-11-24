import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Container, Navbar, Nav } from 'react-bootstrap';
import Visitors from './Visitors';
import QA from './QA';
import Display from './Display';

function App() {
  return (
    <Router>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand href="/">API Test Application</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav>
              <NavLink to="/visitors" className="nav-link">Посетители</NavLink>
              <NavLink to="/qa" className="nav-link">Вопросы и Ответы</NavLink>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <Container className="mt-4">
        <Routes>
          <Route path="/visitors" element={<Visitors />} />
          <Route path="/qa" element={<QA />} />
          <Route path="*" element={<Visitors />} />
        </Routes>
        <Display />
      </Container>
    </Router>
  );
}

export default App;
