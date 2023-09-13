// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import { Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import * as React from 'react';
import { TableOfContents } from './toc';
import { TOCItem } from './toc_item';
import { IHeading, ITableOfContentsRegistry as Registry } from './tokens';

/**
 * Interface describing component properties.
 *
 * @private
 */
interface IProperties {
  /**
   * Display title.
   */
  title: string;

  /**
   * List of headings to render.
   */
  toc: IHeading[];

  /**
   * Toolbar.
   */
  toolbar: any;

  entryClicked?: Signal<TableOfContents, TOCItem>;

  /**
   * Table of contents generator.
   */
  generator: Registry.IGenerator<Widget> | null;

  /**
   * Renders a heading item.
   *
   * @param item - heading
   * @param toc - list of headings in toc to use for rendering current position
   * @returns rendered heading
   */
  itemRenderer: (item: IHeading, toc: IHeading[]) => JSX.Element | null;
}

/**
 * Interface describing component state.
 *
 * @private
 */
interface IState {}

/**
 * React component for a table of contents tree.
 *
 * @private
 */
class TOCTree extends React.Component<IProperties, IState> {
  /**
   * Renders a table of contents tree.
   */
  render(): JSX.Element {
    const Toolbar = this.props.toolbar;

    // Map the heading objects onto a list of JSX elements...
    let i = 0;
    const list: JSX.Element[] = this.props.toc.map(el => {
      return (
        <TOCItem
          heading={el}
          toc={this.props.toc}
          entryClicked={this.props.entryClicked}
          itemRenderer={this.props.itemRenderer}
          key={`${el.text}-${el.level}-${i++}`}
        />
      );
    });
    return (
      <div className="jpcodetoc-TableOfContents">
        <div className="jpcodetoc-stack-panel-header">{this.props.title}</div>
        {Toolbar && <Toolbar />}
        <ul className="jpcodetoc-TableOfContents-content">{list}</ul>
      </div>
    );
  }
}

/**
 * Exports.
 */
export { TOCTree };
