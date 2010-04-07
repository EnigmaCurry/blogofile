<%def name="filter(chain)">
  ${bf.filter.run_chain(chain, capture(caller.body))}
</%def>

${next.body()}
