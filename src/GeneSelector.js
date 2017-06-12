import React from "react";
//import ReactDOM from "react-dom";
import Autocomplete from "react-autocomplete";
import * as axios from "axios";
import "./GeneSelector.css";

const styles = {
  item: {
    padding: "2px 6px",
    cursor: "default"
  },

  highlightedItem: {
    color: "white",
    background: "hsl(200, 50%, 50%)",
    padding: "2px 6px",
    cursor: "default"
  },

  menu: {
    border: "solid 1px #ccc"
  }
};

export class GeneSelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: "",
      genes: [],
      loading: false,
      selectHandler: props.selectHandler
    };
  }

  render() {
    return (
      <div className="GeneSelector">
        <label htmlFor="genes-autocomplete">Search for genes: </label>
        <Autocomplete
          inputProps={{ id: "genes-autocomplete" }}
          ref="autocomplete"
          value={this.state.value}
          items={this.state.genes}
          getItemValue={item => item}
          onSelect={(value, item) => {
            const { selectHandler } = this.state;
            this.setState({ value, genes: [item] });
            selectHandler(value);
          }}
          onChange={(event, value) => {
            this.setState({ value });
            let that = this;
            if (!this.state.loading && value.length >= 2) {
              this.setState({ loading: true });
              axios
                .get(`/suggestions?gene=${value}`)
                .then(function(response) {
                  that.setState({ genes: response.data, loading: false });
                })
                .catch(function(error) {
                  console.log(error);
                });
            }
          }}
          renderItem={(item, isHighlighted) => (
            <div
              style={isHighlighted ? styles.highlightedItem : styles.item}
              key={item}
              id={item}
            >
              {item}
            </div>
          )}
        />
      </div>
    );
  }
}
