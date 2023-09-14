// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import { INotebookHeading } from '../../tokens';

/**
 * Returns a boolean indicating whether a heading is filtered out by selected tags.
 *
 * @private
 * @param heading - notebook heading
 * @param tags - list of tags
 * @returns boolean indicating whether a heading is filtered
 */
function isHeadingFiltered(heading: INotebookHeading, tags: string[]): boolean {
  if (tags.length === 0) {
    return false;
  }
  if (heading && heading.cellRef) {
    const ctags = heading.cellRef.model.getMetadata('tags') as string[];
    if (ctags) {
      for (let j = 0; j < ctags.length; j++) {
        const name = ctags[j];
        for (let k = 0; k < tags.length; k++) {
          if (tags[k] === name) {
            return false;
          }
        }
      }
    }
  }
  return true;
}

/**
 * Exports.
 */
export { isHeadingFiltered };
