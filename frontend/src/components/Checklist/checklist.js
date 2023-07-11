import React, { Component, useState } from "react";
import ReactDOM from "react-dom";
import { default as ReactSelect } from "react-select";
import Select from 'react-select';
import "../style.css";
import { components } from "react-select";

const stations = [
  { value: "GMJI", label: "GMJI" },
  { value: "JAGI", label: "JAGI" },
  { value: "PWJI", label: "PWJI" }
];
const Option = (props) => {
  return (
    <div>
      <components.Option {...props}>
        <input
          type="checkbox"
          checked={props.isSelected}
          onChange={() => null}
        />{" "}
        <label>{props.label}</label>
      </components.Option>
    </div>
  );
};

const Checklist = (props) => {

  

  const handleChange = (selected) => {
    let selectList = []
    for(var i=0;i<selected.length;i++){
      selectList.push(selected[i].value)
    }
    props.stateChanger(selectList);
    props.setOptionSelected(selected);
    
  };

  const deselect = (selected) => {
    console.log(selected);
  }

  return (
      <form
        data-testid="checklist"
      >
        <label htmlFor="checklist">Checklist</label>
        <Select
          data-testid="station"
          placeholder="Please select station(s)"
          defaultValue=""
          options={stations}
          isMulti
          deselect-option={deselect}
          closeMenuOnSelect={false}
          hideSelectedOptions={false}
          components={{
            Option
          }}
          name="checklist"
          inputId='checklist'
          onChange={handleChange}
          allowSelectAll={true}
          value={props.optionSelected}
        />
      </form>
    );
}

export default Checklist;
