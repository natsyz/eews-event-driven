import { getByTestId, render, screen, fireEvent, waitFor, getByText, within} from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import AdminMap from '../AdminMap';
import { select } from "react-select-event";
import WS from "jest-websocket-mock";
const { ResizeObserver } = window;
import mseed1 from './samples';

beforeEach(() => {
    //@ts-ignore
    delete window.ResizeObserver;
    window.ResizeObserver = jest.fn().mockImplementation(() => ({
      observe: jest.fn(),
      unobserve: jest.fn(),
      disconnect: jest.fn(),
    }));
  });
  
  afterEach(() => {
    window.ResizeObserver = ResizeObserver;
    jest.restoreAllMocks();
  });

test("React Select works!", async () => {
    const { getByTestId, getByLabelText} = render(<AdminMap/>);
    expect(getByTestId("dropdown")).toHaveFormValues({ dropdown: '' });
    expect(getByTestId("checklist")).toHaveFormValues({ checklist: "" });
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist")
  
    // select two values...
    await select(dropdown, "20090118_064750");
    expect(getByTestId("dropdown")).toHaveFormValues({ dropdown: '20090118_064750' });
    await select(checklist, ["GMJI"])
    expect(getByTestId("checklist")).toHaveFormValues({ checklist: "GMJI" });
    expect(getByTestId("GMJI"));
  });

  test("Dapat memuat Chart GMJI saja", async () => {
    const { getByTestId, getByLabelText} = render(<AdminMap/>);
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist")
  
    await select(dropdown, "20090118_064750");
    await select(checklist, ["GMJI"])
    expect(getByTestId("GMJI"));
  });

  test("Dapat memuat Chart PWJI saja", async () => {
    const { getByTestId, getByLabelText} = render(<AdminMap/>);
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist")
  
    await select(dropdown, "20090118_064750");
    await select(checklist, ["PWJI"])
    expect(getByTestId("PWJI"));
  });

  test("Dapat memuat Chart JAGI saja", async () => {
    const { getByTestId, getByLabelText} = render(<AdminMap/>);
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist")
  
    await select(dropdown, "20090118_064750");
    await select(checklist, ["JAGI"])
    expect(getByTestId("JAGI"));
  });

  test("Dapat memuat Chart GMJI dan JAGI saja", async () => {
    const { getByTestId, getByLabelText} = render(<AdminMap/>);
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist")
  
    await select(dropdown, "20090118_064750");
    await select(checklist, ["GMJI","JAGI"])
    expect(getByTestId("GMJI"));
    expect(getByTestId("JAGI"));
  });

  test("Dapat memuat Chart GMJI dan PWJI saja", async () => {
    const { getByTestId, getByLabelText} = render(<AdminMap/>);
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist")
  
    await select(dropdown, "20090118_064750");
    await select(checklist, ["GMJI","PWJI"])
    expect(getByTestId("GMJI"));
    expect(getByTestId("PWJI"));
  });

  test("Dapat memuat Chart PWJI dan JAGI saja", async () => {
    const { getByTestId, getByLabelText} = render(<AdminMap/>);
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist")
  
    await select(dropdown, "20090118_064750");
    await select(checklist, ["JAGI","PWJI"])
    expect(getByTestId("JAGI"));
    expect(getByTestId("PWJI"))
  });

  test("Dapat memuat Chart GMJI, JAGI, PWJI ", async () => {
    const { getByTestId, getByLabelText} = render(<AdminMap/>);
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist")
  
    await select(dropdown, "20090118_064750");
    await select(checklist, ["GMJI","PWJI","JAGI"])
    expect(getByTestId("GMJI"));
    expect(getByTestId("JAGI"));
    expect(getByTestId("PWJI"));
  });



test("Dapat menghapus chart GMJI", async () => {
    const { getByTestId, getByLabelText, getByRole, queryByTestId, getByText} = render(<AdminMap/>);
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist");

    await select(dropdown, "20090118_064750");
    await select(checklist, ["GMJI"]);
    expect(getByTestId("GMJI"));
    const button = getByRole('button', {name: 'Remove GMJI'});
    fireEvent.click(button); 
    expect(queryByTestId("GMJI")).toBeNull();
    
});

test("Dapat menghapus chart JAGI", async () => {
    const { getByTestId, getByLabelText, getByRole, queryByTestId, getByText} = render(<AdminMap/>);
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist");

    await select(dropdown, "20090118_064750");
    await select(checklist, ["JAGI"]);
    expect(getByTestId("JAGI"));
    const button = getByRole('button', {name: 'Remove JAGI'});
    fireEvent.click(button); 
    expect(queryByTestId("JAGI")).toBeNull();
    
});

test("Dapat menghapus chart PWJI", async () => {
    const { getByTestId, getByLabelText, getByRole, queryByTestId, getByText} = render(<AdminMap/>);
    const dropdown = getByLabelText('Mseed');
    const checklist = getByLabelText("Checklist");

    await select(dropdown, "20090118_064750");
    await select(checklist, ["PWJI"]);
    expect(getByTestId("PWJI"));
    const button = getByRole('button', {name: 'Remove PWJI'});
    fireEvent.click(button); 
    expect(queryByTestId("PWJI")).toBeNull();
    
});

jest.useRealTimers();
test("the mock server sends messages to connected clients", async () => {
  const server = new WS("wss://localhost:8000/get_gmji_data/20090118_064750/");
  const { getByTestId, getByLabelText, getByRole, queryByTestId, getByText} = render(<AdminMap url={'localhost:8000'}/>);
  const dropdown = getByLabelText('Mseed');
  const checklist = getByLabelText("Checklist");
  await select(dropdown, "20090118_064750");
  await server.connected;
  await select(checklist, ["GMJI"]);
  server.send(JSON.stringify(mseed1[0]));
  expect(getByTestId("20090118_064750"));
  const server2 = new WS("wss://localhost:8000/get_gmji_data/20090119_211141/");
  await select(dropdown, "20090119_211141");
  await server2.connected;
  server2.send(JSON.stringify(mseed1[1]));
  expect(getByTestId("20090119_211141"));
});

test("the mock server sends messages to connected clients", async () => {
  const server = new WS("wss://localhost:8000/get_gmji_data/20100208_112154/");
  const { getByTestId, getByLabelText, getByRole, queryByTestId, getByText} = render(<AdminMap url={'localhost:8000'}/>);
  const dropdown = getByLabelText('Mseed');
  const checklist = getByLabelText("Checklist");
  await select(dropdown, "20100208_112154");
  await server.connected;
  await select(checklist, ["GMJI"]);
  server.send(JSON.stringify(mseed1[2]));
  expect(getByTestId("20100208_112154"));
});

test("the mock server sends messages to connected clients", async () => {
  const server = new WS("wss://localhost:8000/get_gmji_data/20120915_163224/");
  const { getByTestId, getByLabelText, getByRole, queryByTestId, getByText} = render(<AdminMap url={'localhost:8000'}/>);
  const dropdown = getByLabelText('Mseed');
  const checklist = getByLabelText("Checklist");
  await select(dropdown, "20120915_163224");
  await server.connected;
  await select(checklist, ["GMJI"]);
  server.send(JSON.stringify(mseed1[3]));
  expect(getByTestId("20120915_163224"));
});