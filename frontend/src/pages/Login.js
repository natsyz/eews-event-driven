import React, { useEffect, useState } from "react";
import {
    MDBContainer,
    MDBInput,
    MDBCheckbox,
    MDBBtn,
    MDBIcon
} from 'mdb-react-ui-kit';
import { Link, useNavigate } from "react-router-dom";
import { auth, logInWithEmailAndPassword } from "../firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import "./Login.css";

function Login() {  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, loading, error] = useAuthState(auth);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate("/admin-map");
  }, [user, loading]);
  
  return (
        <MDBContainer className="p-3 my-5 d-flex flex-column w-50">
            <h2 className="fw-bold mb-2 text-uppercase">Login</h2>
            <br></br>
            <MDBInput wrapperClass='mb-4' label='Email address' id='form1' type='email' value={email} onChange={(e) => setEmail(e.target.value)}/>
            <MDBInput wrapperClass='mb-4' label='Password' id='form2' type='password' value={password} onChange={(e) => setPassword(e.target.value)}/>
            <br></br>
            <MDBBtn className="mb-4" onClick={() => logInWithEmailAndPassword(email, password)}>Sign in</MDBBtn>
        </MDBContainer>
   
    
  );
}

export default Login;