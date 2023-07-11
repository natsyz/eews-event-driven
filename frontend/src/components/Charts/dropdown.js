import React, { useState } from 'react';

import Select from 'react-select';
import "../style.css";

const urls = [
  { value: "20090118_064750", label: "20090118_064750" },
  { value: "20090119_211141", label: "20090119_211141" },
  { value: "20100208_112154", label: "20100208_112154" },
  { value: "20120915_163224", label: "20120915_163224" }
];

const Dropdown = (props) => {
  const handleChange = (selected) => {
    props.stateChanger(selected);
    props.setMseedSelected(selected);
    
  };
  return (
    <form data-testid="dropdown">
      <label htmlFor="dropdown">Mseed</label>
      <Select
      data-testid="url"
      placeholder="Please select Mseed"
        className="basic-single"
        classNamePrefix="select"
        defaultValue={''}
        name="dropdown"
        inputId='dropdown'
        options={urls}
        onChange={handleChange}
      />
    </form>
  );
};

export default Dropdown;