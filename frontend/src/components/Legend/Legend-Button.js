import React, { useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Overlay from 'react-bootstrap/Overlay';
import '../style.css'
export default function Legend() {
  const [show, setShow] = useState(false);
  const target = useRef(null);

  return (
    <>
      <Button variant="light" ref={target} onClick={() => setShow(!show)}>
        <img src={require('../../assets/icons8-key-24.png')}></img> 
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
              <div className='legend-item'>
                <img src={require('../../assets/marker-icon.png')}></img>
                <div className='legend-text'>Stasiun Offline</div>
              </div>
              <div className='legend-item'>
                <img src={require('../../assets/red-marker.png')}></img>
                <div className='legend-text'>Stasiun Online</div>
              </div>
              <div className='legend-item'>
                <div  >
                  <img src={require('../../assets/red-circle24.png')}></img>
                </div>
                <div className='legend-text'>Sumber Gempa</div>
              </div>
            </div>
          </div>
        )}
      </Overlay>
    </>
  );
}
