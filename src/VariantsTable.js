import { Get } from "react-axios";
import React from "react";
//import ReactDOM from "react-dom";
import { Column, Table } from "react-virtualized";
import "react-virtualized/styles.css";

export class VariantsTable extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      gene: props.gene
    };
  }

  componentDidMount() {}

  componentDidUpdate(prevProps, prevState) {
    const { props } = this;
    if (props.gene !== prevState.gene) {
      this.setState({ gene: props.gene });
    }
  }

  render() {
    const { gene } = this.state;
    if (!gene) {
      return <div />;
    }
    return (
      <div>
        <Get url={`/variants?gene=${gene}`}>
          {(error, response, isLoading) => {
            if (error) {
              return <div>Error retrieving variant data: {error.message}</div>;
            } else if (isLoading) {
              return <div>Loading...</div>;
            } else if (response !== null) {
              const list = response.data;
              const columns = [
                {
                  name: "Gene",
                  width: 80
                },
                {
                  name: "Nucleotide Change",
                  width: 380
                },
                {
                  name: "Protein Change",
                  width: 200
                },
                {
                  name: "Alias",
                  width: 180
                },
                {
                  name: "Region",
                  width: 200
                },
                {
                  name: "Reported Classification",
                  width: 300
                },
                {
                  name: "Last Evaluated",
                  width: 160
                },
                {
                  name: "Last Updated",
                  width: 140
                },
                {
                  name: "More Info",
                  width: 100,
                  isUri: true
                }
              ];
              const tableWidth = columns.reduce(function(acc, column) {
                return acc + column.width;
              }, 0);
              return (
                <Table
                  width={tableWidth}
                  height={600}
                  headerHeight={20}
                  rowHeight={30}
                  rowCount={list.length}
                  rowGetter={({ index }) => list[index]}
                >
                  {columns.map(function(column) {
                    if (column.isUri) {
                      return (
                        <Column
                          label={column.name}
                          key={column.name}
                          dataKey={column.name}
                          width={column.width}
                          cellRenderer={function({
                            cellData,
                            columnData,
                            columnIndex,
                            dataKey,
                            isScrolling,
                            rowData,
                            rowIndex
                          }) {
                            if (cellData == null) {
                              return "";
                            } else {
                              return <a href={cellData}>More Info</a>;
                            }
                          }}
                        />
                      );
                    }
                    return (
                      <Column
                        label={column.name}
                        key={column.name}
                        dataKey={column.name}
                        width={column.width}
                      />
                    );
                  })}
                </Table>
              );
            }
            return <div>Default message before request is made.</div>;
          }}
        </Get>
      </div>
    );
  }
}
