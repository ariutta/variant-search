import React, { Component } from "react";
import "./App.css";
import { GeneSelector } from "./GeneSelector";
import { VariantsTable } from "./VariantsTable";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      gene: null
    };
  }

  render() {
    return (
      <div className="App">
        <div className="App-header">
          <h1>Database of clinically-observed genetic variants</h1>
        </div>
        <GeneSelector
          selectHandler={value => {
            this.setState({ gene: value });
          }}
        />
        <VariantsTable gene={this.state.gene} />
      </div>
    );
  }
}

export default App;
