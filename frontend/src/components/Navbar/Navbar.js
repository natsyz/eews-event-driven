import React, { useEffect, useState } from "react";
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import { auth, db, logout } from '../../firebase'
import '../style.css'

function Navibar() {
  const [user, loading, error] = useAuthState(auth);
  const [name, setName] = useState("");
  const navigate = useNavigate();

  return (
    <Navbar expand="lg" className='bg-custom'>
      <Container className='container-lg'>
        <Navbar.Brand href="/">EEWS</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link href="/">Map</Nav.Link>
            {/* <Nav.Link href="/help">Help</Nav.Link>
            <Nav.Link href="/about">About</Nav.Link> */}
            {user ?<Nav.Link href="/admin-map">Admin</Nav.Link> : null}
          </Nav>
          <Nav>
            {user ? <Nav.Link href="/" onClick={logout}>Log Out</Nav.Link> : null}
            {!user ? <Nav.Link href="/login">Log In</Nav.Link> : null}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default Navibar;