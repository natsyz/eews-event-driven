import React, { useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Overlay from 'react-bootstrap/Overlay';
import '../style.css'
export default function Performance(props) {
  const [show, setShow] = useState(false);
  const target = useRef(null);

  return (
    <>
      <Button variant="light" ref={target} onClick={() => setShow(!show)}>
        <img src={require('../../assets/performance.png')}></img> 
      </Button>
      <Overlay target={target.current} show={show} placement="left-start">
        {({ placement, arrowProps, show: _show, popper, ...props }) => (
          <div
            {...props}
            style={{
              position: 'absolute',
              zIndex:800,
              backgroundColor: 'white',
              padding: '30px 20px',
              color: 'black',
              borderRadius: 3,
              ...props.style,
            }}
          >
            <div className='legend-contents'>
              {/* <h>Algorithm performance from last prediction</h>
              <br></br> */}
              {/* <div className='legend-item'>
                STA/LTA : 289 ms
              </div> */}
              <div className='legend-item'>
                Time from P-Arrival detection to MTR Results : {props.predData-props.arrivalData} ms
              </div>
              <div className='legend-item'>
                
              </div>
            </div>
          </div>
        )}
      </Overlay>
    </>
  );
}
