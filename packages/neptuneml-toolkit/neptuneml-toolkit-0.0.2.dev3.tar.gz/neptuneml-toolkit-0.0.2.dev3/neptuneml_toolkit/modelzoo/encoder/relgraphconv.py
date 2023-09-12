class EdgeRelGraphConv(nn.Module):
    r"""Relational graph convolution layer.

    Relational graph convolution is introduced in "`Modeling Relational Data with Graph
    Convolutional Networks <https://arxiv.org/abs/1703.06103>`__"
    and can be described as below:

    .. math::

       h_i^{(l+1)} = \sigma(\sum_{r\in\mathcal{R}}
       \sum_{j\in\mathcal{N}^r(i)}\frac{1}{c_{i,r}}W_r^{(l)}h_j^{(l)}+W_0^{(l)}h_i^{(l)})

    where :math:`\mathcal{N}^r(i)` is the neighbor set of node :math:`i` w.r.t. relation
    :math:`r`. :math:`c_{i,r}` is the normalizer equal
    to :math:`|\mathcal{N}^r(i)|`. :math:`\sigma` is an activation function. :math:`W_0`
    is the self-loop weight.

    The basis regularization decomposes :math:`W_r` by:

    .. math::

       W_r^{(l)} = \sum_{b=1}^B a_{rb}^{(l)}V_b^{(l)}

    where :math:`B` is the number of bases, :math:`V_b^{(l)}` are linearly combined
    with coefficients :math:`a_{rb}^{(l)}`.

    The block-diagonal-decomposition regularization decomposes :math:`W_r` into :math:`B`
    number of block diagonal matrices. We refer :math:`B` as the number of bases.

    The block regularization decomposes :math:`W_r` by:

    .. math::

       W_r^{(l)} = \oplus_{b=1}^B Q_{rb}^{(l)}

    where :math:`B` is the number of bases, :math:`Q_{rb}^{(l)}` are block
    bases with shape :math:`R^{(d^{(l+1)}/B)*(d^{l}/B)}`.

    Parameters
    ----------
    in_feat : int
        Input feature size; i.e, the number of dimensions of :math:`h_j^{(l)}`.
    out_feat : int
        Output feature size; i.e., the number of dimensions of :math:`h_i^{(l+1)}`.
    num_rels : int
        Number of relations.
    active_rels: list[int]
        Relations that are active for layer
    regularizer : str
        Which weight regularizer to use "basis" or "bdd".
        "basis" is short for basis-diagonal-decomposition.
        "bdd" is short for block-diagonal-decomposition.
    num_bases : int, optional
        Number of bases. If is none, use number of relations. Default: ``None``.
    bias : bool, optional
        True if bias is added. Default: ``True``.
    activation : callable, optional
        Activation function. Default: ``None``.
    self_loop : bool, optional
        True to include self loop message. Default: ``True``.
    low_mem : bool, optional
        True to use low memory implementation of relation message passing function. Default: False.
        This option trades speed with memory consumption, and will slowdown the forward/backward.
        Turn it on when you encounter OOM problem during training or evaluation. Default: ``False``.
    dropout : float, optional
        Dropout rate. Default: ``0.0``
    layer_norm: float, optional
        Add layer norm. Default: ``False``
    edge_dim : int
        The dimension for the edge transformed features. If None then the layer behaves as the original RGCN
        otherwise it will take into account the edge features as dictated by edge_aggregation_type
    edge_aggregation_type :
        Type of aggregation done for the edge transformed features it can anything from "sum", "product", "concat"

    Examples
    --------
    >>> import dgl
    >>> import numpy as np
    >>> import torch as th
    >>> from dgl.nn import RelGraphConv
    >>>
    >>> g = dgl.graph(([0,1,2,3,2,5], [1,2,3,4,0,3]))
    >>> feat = th.ones(6, 10)
    >>> conv = RelGraphConv(10, 2, 3, regularizer='basis', num_bases=2)
    >>> conv.weight.shape
    torch.Size([2, 10, 2])
    >>> etype = th.tensor(np.array([0,1,2,0,1,2]).astype(np.int64))
    >>> res = conv(g, feat, etype)
    >>> res
    tensor([[ 0.3996, -2.3303],
            [-0.4323, -0.1440],
            [ 0.3996, -2.3303],
            [ 2.1046, -2.8654],
            [-0.4323, -0.1440],
            [-0.1309, -1.0000]], grad_fn=<AddBackward0>)

    >>> # One-hot input
    >>> one_hot_feat = th.tensor(np.array([0,1,2,3,4,5]).astype(np.int64))
    >>> res = conv(g, one_hot_feat, etype)
    >>> res
    tensor([[ 0.5925,  0.0985],
            [-0.3953,  0.8408],
            [-0.9819,  0.5284],
            [-1.0085, -0.1721],
            [ 0.5962,  1.2002],
            [ 0.0365, -0.3532]], grad_fn=<AddBackward0>)
    """
    def __init__(self,
                 in_feat,
                 out_feat,
                 num_rels,
                 active_rels=None,
                 regularizer="basis",
                 num_bases=None,
                 bias=True,
                 activation=None,
                 self_loop=True,
                 low_mem=False,
                 dropout=0.0,
                 edge_dim=None,
                 edge_aggregation_type="sum",
                 layer_norm=False):class EdgeRelGraphConv(nn.Module):
    r"""Relational graph convolution layer.

    Relational graph convolution is introduced in "`Modeling Relational Data with Graph
    Convolutional Networks <https://arxiv.org/abs/1703.06103>`__"
    and can be described as below:

    .. math::

       h_i^{(l+1)} = \sigma(\sum_{r\in\mathcal{R}}
       \sum_{j\in\mathcal{N}^r(i)}\frac{1}{c_{i,r}}W_r^{(l)}h_j^{(l)}+W_0^{(l)}h_i^{(l)})

    where :math:`\mathcal{N}^r(i)` is the neighbor set of node :math:`i` w.r.t. relation
    :math:`r`. :math:`c_{i,r}` is the normalizer equal
    to :math:`|\mathcal{N}^r(i)|`. :math:`\sigma` is an activation function. :math:`W_0`
    is the self-loop weight.

    The basis regularization decomposes :math:`W_r` by:

    .. math::

       W_r^{(l)} = \sum_{b=1}^B a_{rb}^{(l)}V_b^{(l)}

    where :math:`B` is the number of bases, :math:`V_b^{(l)}` are linearly combined
    with coefficients :math:`a_{rb}^{(l)}`.

    The block-diagonal-decomposition regularization decomposes :math:`W_r` into :math:`B`
    number of block diagonal matrices. We refer :math:`B` as the number of bases.

    The block regularization decomposes :math:`W_r` by:

    .. math::

       W_r^{(l)} = \oplus_{b=1}^B Q_{rb}^{(l)}

    where :math:`B` is the number of bases, :math:`Q_{rb}^{(l)}` are block
    bases with shape :math:`R^{(d^{(l+1)}/B)*(d^{l}/B)}`.

    Parameters
    ----------
    in_feat : int
        Input feature size; i.e, the number of dimensions of :math:`h_j^{(l)}`.
    out_feat : int
        Output feature size; i.e., the number of dimensions of :math:`h_i^{(l+1)}`.
    num_rels : int
        Number of relations.
    active_rels: list[int]
        Relations that are active for layer
    regularizer : str
        Which weight regularizer to use "basis" or "bdd".
        "basis" is short for basis-diagonal-decomposition.
        "bdd" is short for block-diagonal-decomposition.
    num_bases : int, optional
        Number of bases. If is none, use number of relations. Default: ``None``.
    bias : bool, optional
        True if bias is added. Default: ``True``.
    activation : callable, optional
        Activation function. Default: ``None``.
    self_loop : bool, optional
        True to include self loop message. Default: ``True``.
    low_mem : bool, optional
        True to use low memory implementation of relation message passing function. Default: False.
        This option trades speed with memory consumption, and will slowdown the forward/backward.
        Turn it on when you encounter OOM problem during training or evaluation. Default: ``False``.
    dropout : float, optional
        Dropout rate. Default: ``0.0``
    layer_norm: float, optional
        Add layer norm. Default: ``False``
    edge_dim : int
        The dimension for the edge transformed features. If None then the layer behaves as the original RGCN
        otherwise it will take into account the edge features as dictated by edge_aggregation_type
    edge_aggregation_type :
        Type of aggregation done for the edge transformed features it can anything from "sum", "product", "concat"

    Examples
    --------
    >>> import dgl
    >>> import numpy as np
    >>> import torch as th
    >>> from dgl.nn import RelGraphConv
    >>>
    >>> g = dgl.graph(([0,1,2,3,2,5], [1,2,3,4,0,3]))
    >>> feat = th.ones(6, 10)
    >>> conv = RelGraphConv(10, 2, 3, regularizer='basis', num_bases=2)
    >>> conv.weight.shape
    torch.Size([2, 10, 2])
    >>> etype = th.tensor(np.array([0,1,2,0,1,2]).astype(np.int64))
    >>> res = conv(g, feat, etype)
    >>> res
    tensor([[ 0.3996, -2.3303],
            [-0.4323, -0.1440],
            [ 0.3996, -2.3303],
            [ 2.1046, -2.8654],
            [-0.4323, -0.1440],
            [-0.1309, -1.0000]], grad_fn=<AddBackward0>)

    >>> # One-hot input
    >>> one_hot_feat = th.tensor(np.array([0,1,2,3,4,5]).astype(np.int64))
    >>> res = conv(g, one_hot_feat, etype)
    >>> res
    tensor([[ 0.5925,  0.0985],
            [-0.3953,  0.8408],
            [-0.9819,  0.5284],
            [-1.0085, -0.1721],
            [ 0.5962,  1.2002],
            [ 0.0365, -0.3532]], grad_fn=<AddBackward0>)
    """
    def __init__(self,
                 in_feat,
                 out_feat,
                 num_rels,
                 active_rels=None,
                 regularizer="basis",
                 num_bases=None,
                 bias=True,
                 activation=None,
                 self_loop=True,
                 low_mem=False,
                 dropout=0.0,
                 edge_dim=None,
                 edge_aggregation_type="sum",
                 layer_norm=False):
        super(EdgeRelGraphConv, self).__init__()
        self.in_feat = in_feat
        self.out_feat = out_feat
        self.num_rels = num_rels
        self.regularizer = regularizer
        self.num_bases = num_bases
        self.active_rels = range(num_rels) if active_rels is None else active_rels
        if self.num_bases is None or self.num_bases > self.num_rels or self.num_bases <= 0:
            self.num_bases = self.num_rels
        self.bias = bias
        self.activation = activation
        self.self_loop = self_loop
        self.low_mem = low_mem
        self.layer_norm = layer_norm
        self.edge_dim =edge_dim
        self.edge_aggregation_type = edge_aggregation_type

        if regularizer == "basis":
            # add basis weights
            self.weight = nn.Parameter(th.Tensor(self.num_bases, self.in_feat, self.out_feat))
            if self.num_bases < self.num_rels:
                # linear combination coefficients
                self.w_comp = nn.Parameter(th.Tensor(self.num_rels, self.num_bases))
            nn.init.xavier_uniform_(self.weight, gain=nn.init.calculate_gain('relu'))
            if self.num_bases < self.num_rels:
                nn.init.xavier_uniform_(self.w_comp,
                                        gain=nn.init.calculate_gain('relu'))
            # message func
            self.message_func = self.basis_message_func
        elif regularizer == "bdd":
            if in_feat % self.num_bases != 0 or out_feat % self.num_bases != 0:
                raise ValueError(
                    'Feature size must be a multiplier of num_bases (%d).'
                    % self.num_bases
                )
            # add block diagonal weights
            self.submat_in = in_feat // self.num_bases
            self.submat_out = out_feat // self.num_bases

            # assuming in_feat and out_feat are both divisible by num_bases
            self.weight = nn.Parameter(th.Tensor(
                self.num_rels, self.num_bases * self.submat_in * self.submat_out))
            nn.init.xavier_uniform_(self.weight, gain=nn.init.calculate_gain('relu'))
            # message func
            self.message_func = self.bdd_message_func
        else:
            raise ValueError("Regularizer must be either 'basis' or 'bdd'")

        # bias
        if self.bias:
            self.h_bias = nn.Parameter(th.Tensor(out_feat))
            nn.init.zeros_(self.h_bias)

        # layer norm
        if self.layer_norm:
            self.layer_norm_weight = nn.LayerNorm(out_feat, elementwise_affine=True)

        # weight for self loop
        if self.self_loop:
            self.loop_weight = nn.Parameter(th.Tensor(in_feat, out_feat))
            nn.init.xavier_uniform_(self.loop_weight,
                                    gain=nn.init.calculate_gain('relu'))
        if edge_dim is not None:
            self.edge_feat_transform_weight= nn.Linear(self.edge_dim if self.edge_aggregation_type
                                            != "concat" else self.edge_dim+self.out_feat,self.out_feat)
        self.dropout = nn.Dropout(dropout)

    def edge_feat_transform(self, msg, edge_feats):
        type = self.edge_aggregation_type
        if type== "sum":
            msg = msg + self.edge_feat_transform_weight(edge_feats)
        elif type == "product":
            msg = msg * self.edge_feat_transform_weight(edge_feats)
        elif type == "concat":
            msg =  self.edge_feat_transform_weight(th.cat((edge_feats,msg),dim=1))
        else:
            raise TypeError('Not supported message aggregate  type.')
        return msg

    def basis_message_func(self, edges, etypes):
        """Message function for basis regularizer.

        Parameters
        ----------
        edges : dgl.EdgeBatch
            Input to DGL message UDF.
        etypes : torch.Tensor or list[int]
            Edge type data. Could be either:

                * An :math:`(|E|,)` dense tensor. Each element corresponds to the edge's type ID.
                  Preferred format if ``lowmem == False``.
                * An integer list. The i^th element is the number of edges of the i^th type.
                  This requires the input graph to store edges sorted by their type IDs.
                  Preferred format if ``lowmem == True``.
        """
        if self.num_bases < self.num_rels:
            # generate all weights from bases
            weight = self.weight.view(self.num_bases,
                                      self.in_feat * self.out_feat)
            weight = th.matmul(self.w_comp, weight).view(
                self.num_rels, self.in_feat, self.out_feat)
        else:
            weight = self.weight

        h = edges.src['h']
        device = h.device

        if h.shape[0] == 0:
            return {'msg': th.tensor((), device=device)}

        if h.dtype == th.int64 and h.ndim == 1:
            # Each element is the node's ID. Use index select: weight[etypes, h, :]
            # The following is a faster version of it.
            if isinstance(etypes, list):
                etypes = th.repeat_interleave(th.arange(len(etypes), device=device),
                                              th.tensor(etypes, device=device))
            weight = weight.view(-1, weight.shape[2])
            flatidx = etypes * weight.shape[1] + h
            msg = weight.index_select(0, flatidx)
        elif self.low_mem:
            # A more memory-friendly implementation.
            # Calculate msg @ W_r before put msg into edge.
            assert isinstance(etypes, list)
            h_t = th.split(h, etypes)
            msg = []
            for etype in range(self.num_rels):
                if h_t[etype].shape[0] == 0:
                    continue
                if etype in self.active_rels: # check if this etype is active
                    msg.append(th.zeros(h_t[etype].shape))
                else:
                    msg.append(th.matmul(h_t[etype], weight[etype]))
            msg = th.cat(msg)
        else:
            # Use batched matmult
            active_idx = th.nonzero(edges.data["mask"]).squeeze()
            msg = th.zeros(h.shape[0], self.out_feat, device=device)
            if isinstance(etypes, list):
                etypes = th.repeat_interleave(th.arange(len(etypes), device=device),
                                              th.tensor(etypes, device=device))
            weight = weight.index_select(0, etypes)
            msg[active_idx] = th.bmm(h.unsqueeze(1), weight).squeeze(1)[active_idx]

        if 'norm' in edges.data:
            msg = msg * edges.data['norm']
        if 'feat' in edges.data:
            edge_feat_seeds = th.nonzero(th.logical_and(edges.data["efeat_bool"], edges.data["mask"]).int()).squeeze()
            if edge_feat_seeds.shape[0] != 0:
                msg[edge_feat_seeds] = self.edge_feat_transform(msg[edge_feat_seeds],edges.data["feat"][edge_feat_seeds])
        return {'msg': msg}

    def bdd_message_func(self, edges, etypes):
        """Message function for block-diagonal-decomposition regularizer.

        Parameters
        ----------
        edges : dgl.EdgeBatch
            Input to DGL message UDF.
        etypes : torch.Tensor or list[int]
            Edge type data. Could be either:

                * An :math:`(|E|,)` dense tensor. Each element corresponds to the edge's type ID.
                  Preferred format if ``lowmem == False``.
                * An integer list. The i^th element is the number of edges of the i^th type.
                  This requires the input graph to store edges sorted by their type IDs.
                  Preferred format if ``lowmem == True``.
        """
        h = edges.src['h']
        device = h.device

        if h.dtype == th.int64 and h.ndim == 1:
            raise TypeError('Block decomposition does not allow integer ID feature.')

        if self.low_mem:
            # A more memory-friendly implementation.
            # Calculate msg @ W_r before put msg into edge.
            assert isinstance(etypes, list)
            h_t = th.split(h, etypes)
            msg = []
            for etype in range(self.num_rels):
                if h_t[etype].shape[0] == 0:
                    continue
                if etype in self.active_rels: # check if this etype is active
                    msg.append(th.zeros(h_t[etype].shape))
                else:
                    tmp_w = self.weight[etype].view(self.num_bases, self.submat_in, self.submat_out)
                    tmp_h = h_t[etype].view(-1, self.num_bases, self.submat_in)
                    msg.append(th.einsum('abc,bcd->abd', tmp_h, tmp_w).reshape(-1, self.out_feat))
            msg = th.cat(msg)
        else:
            # Use batched matmult
            active_idx = th.nonzero(edges.data["mask"]).squeeze()
            msg = th.zeros(h.shape[0], self.out_feat, device=device)
            if isinstance(etypes, list):
                etypes = th.repeat_interleave(th.arange(len(etypes), device=device),
                                              th.tensor(etypes, device=device))
            weight = self.weight.index_select(0, etypes).view(
                -1, self.submat_in, self.submat_out)
            node = h.view(-1, 1, self.submat_in)
            msg[active_idx] = th.bmm(node, weight).view(-1, self.out_feat)[active_idx]
        if 'norm' in edges.data:
            msg = msg * edges.data['norm']
        if 'feat' in edges.data:
            edge_feat_seeds = th.nonzero(th.logical_and(edges.data["efeat_bool"], edges.data["mask"]).int()).squeeze()
            if edge_feat_seeds.shape[0] != 0:
                msg[edge_feat_seeds] = self.edge_feat_transform(msg[edge_feat_seeds], edges.data["feat"][edge_feat_seeds])
        return {'msg': msg}

    def forward(self, g, feat, etypes, norm=None, edge_feat = None, efeat_bool=None):
        """Forward computation.

        Parameters
        ----------
        g : DGLGraph
            The graph.
        feat : torch.Tensor
            Input node features. Could be either

                * :math:`(|V|, D)` dense tensor
                * :math:`(|V|,)` int64 vector, representing the categorical values of each
                  node. It then treat the input feature as an one-hot encoding feature.
        etypes : torch.Tensor or list[int]
            Edge type data. Could be either

                * An :math:`(|E|,)` dense tensor. Each element corresponds to the edge's type ID.
                  Preferred format if ``lowmem == False``.
                * An integer list. The i^th element is the number of edges of the i^th type.
                  This requires the input graph to store edges sorted by their type IDs.
                  Preferred format if ``lowmem == True``.
        norm : torch.Tensor
            Optional edge normalizer tensor. Shape: :math:`(|E|, 1)`.
        edge_feat : torch.Tensor
            Optional argument for the edge features
        efeat_bool : torch.Tensor
            Optional argument to specify which edges in the batch are associated with features for the rest the layer
            behaves as an RGCN

        Returns
        -------
        torch.Tensor
            New node features.

        Notes
        -----
        Under the ``low_mem`` mode, DGL will sort the graph based on the edge types
        and compute message passing one type at a time. DGL recommends sorts the
        graph beforehand (and cache it if possible) and provides the integer list
        format to the ``etypes`` argument. Use DGL's :func:`~dgl.to_homogeneous` API
        to get a sorted homogeneous graph from a heterogeneous graph. Pass ``return_count=True``
        to it to get the ``etypes`` in integer list.
        """
        if isinstance(etypes, th.Tensor):
            if len(etypes) != g.num_edges():
                raise DGLError('"etypes" tensor must have length equal to the number of edges'
                               ' in the graph. But got {} and {}.'.format(
                                   len(etypes), g.num_edges()))
            if self.low_mem and not (feat.dtype == th.int64 and feat.ndim == 1):
                # Low-mem optimization is not enabled for node ID input. When enabled,
                # it first sorts the graph based on the edge types (the sorting will not
                # change the node IDs). It then converts the etypes tensor to an integer
                # list, where each element is the number of edges of the type.
                # Sort the graph based on the etypes
                sorted_etypes, index = th.sort(etypes)
                g = dgl.edge_subgraph(g, index, relabel_nodes=False)
                # Create a new etypes to be an integer list of number of edges.
                pos = th.searchsorted(sorted_etypes, th.arange(self.num_rels, device=g.device))
                num = th.tensor([len(etypes)], device=g.device)
                etypes = (th.cat([pos[1:], num]) - pos).tolist()
                if norm is not None:
                    norm = norm[index]

        with g.local_scope():
            g.srcdata['h'] = feat
            if norm is not None:
                g.edata['norm'] = norm
            if edge_feat is not None:
                g.edata['feat'] = edge_feat
                g.edata['efeat_bool'] = efeat_bool
            g.edata['mask'] = sum(etypes==i for i in self.active_rels)
            if self.self_loop:
                loop_message = matmul_maybe_select(feat[:g.number_of_dst_nodes()],
                                                   self.loop_weight)
            # message passing
            g.update_all(functools.partial(self.message_func, etypes=etypes),
                         fn.sum(msg='msg', out='h'))

            # apply bias and activation
            if 'h' in g.dstdata and len(g.dstdata['h'].shape) == 2:
                node_repr = g.dstdata['h']
            else:
                node_repr = th.zeros((g.number_of_dst_nodes(), self.out_feat),
                                     dtype=feat.dtype,
                                     device=feat.device)
            if self.layer_norm:
                node_repr = self.layer_norm_weight(node_repr)
            if self.bias:
                node_repr = node_repr + self.h_bias
            if self.self_loop:
                node_repr = node_repr + loop_message
            if self.activation:
                node_repr = self.activation(node_repr)
            node_repr = self.dropout(node_repr)
            return node_repr
        super(EdgeRelGraphConv, self).__init__()
        self.in_feat = in_feat
        self.out_feat = out_feat
        self.num_rels = num_rels
        self.regularizer = regularizer
        self.num_bases = num_bases
        self.active_rels = range(num_rels) if active_rels is None else active_rels
        if self.num_bases is None or self.num_bases > self.num_rels or self.num_bases <= 0:
            self.num_bases = self.num_rels
        self.bias = bias
        self.activation = activation
        self.self_loop = self_loop
        self.low_mem = low_mem
        self.layer_norm = layer_norm
        self.edge_dim =edge_dim
        self.edge_aggregation_type = edge_aggregation_type

        if regularizer == "basis":
            # add basis weights
            self.weight = nn.Parameter(th.Tensor(self.num_bases, self.in_feat, self.out_feat))
            if self.num_bases < self.num_rels:
                # linear combination coefficients
                self.w_comp = nn.Parameter(th.Tensor(self.num_rels, self.num_bases))
            nn.init.xavier_uniform_(self.weight, gain=nn.init.calculate_gain('relu'))
            if self.num_bases < self.num_rels:
                nn.init.xavier_uniform_(self.w_comp,
                                        gain=nn.init.calculate_gain('relu'))
            # message func
            self.message_func = self.basis_message_func
        elif regularizer == "bdd":
            if in_feat % self.num_bases != 0 or out_feat % self.num_bases != 0:
                raise ValueError(
                    'Feature size must be a multiplier of num_bases (%d).'
                    % self.num_bases
                )
            # add block diagonal weights
            self.submat_in = in_feat // self.num_bases
            self.submat_out = out_feat // self.num_bases

            # assuming in_feat and out_feat are both divisible by num_bases
            self.weight = nn.Parameter(th.Tensor(
                self.num_rels, self.num_bases * self.submat_in * self.submat_out))
            nn.init.xavier_uniform_(self.weight, gain=nn.init.calculate_gain('relu'))
            # message func
            self.message_func = self.bdd_message_func
        else:
            raise ValueError("Regularizer must be either 'basis' or 'bdd'")

        # bias
        if self.bias:
            self.h_bias = nn.Parameter(th.Tensor(out_feat))
            nn.init.zeros_(self.h_bias)

        # layer norm
        if self.layer_norm:
            self.layer_norm_weight = nn.LayerNorm(out_feat, elementwise_affine=True)

        # weight for self loop
        if self.self_loop:
            self.loop_weight = nn.Parameter(th.Tensor(in_feat, out_feat))
            nn.init.xavier_uniform_(self.loop_weight,
                                    gain=nn.init.calculate_gain('relu'))
        if edge_dim is not None:
            self.edge_feat_transform_weight= nn.Linear(self.edge_dim if self.edge_aggregation_type
                                            != "concat" else self.edge_dim+self.out_feat,self.out_feat)
        self.dropout = nn.Dropout(dropout)

    def edge_feat_transform(self, msg, edge_feats):
        type = self.edge_aggregation_type
        if type== "sum":
            msg = msg + self.edge_feat_transform_weight(edge_feats)
        elif type == "product":
            msg = msg * self.edge_feat_transform_weight(edge_feats)
        elif type == "concat":
            msg =  self.edge_feat_transform_weight(th.cat((edge_feats,msg),dim=1))
        else:
            raise TypeError('Not supported message aggregate  type.')
        return msg

    def basis_message_func(self, edges, etypes):
        """Message function for basis regularizer.

        Parameters
        ----------
        edges : dgl.EdgeBatch
            Input to DGL message UDF.
        etypes : torch.Tensor or list[int]
            Edge type data. Could be either:

                * An :math:`(|E|,)` dense tensor. Each element corresponds to the edge's type ID.
                  Preferred format if ``lowmem == False``.
                * An integer list. The i^th element is the number of edges of the i^th type.
                  This requires the input graph to store edges sorted by their type IDs.
                  Preferred format if ``lowmem == True``.
        """
        if self.num_bases < self.num_rels:
            # generate all weights from bases
            weight = self.weight.view(self.num_bases,
                                      self.in_feat * self.out_feat)
            weight = th.matmul(self.w_comp, weight).view(
                self.num_rels, self.in_feat, self.out_feat)
        else:
            weight = self.weight

        h = edges.src['h']
        device = h.device

        if h.shape[0] == 0:
            return {'msg': th.tensor((), device=device)}

        if h.dtype == th.int64 and h.ndim == 1:
            # Each element is the node's ID. Use index select: weight[etypes, h, :]
            # The following is a faster version of it.
            if isinstance(etypes, list):
                etypes = th.repeat_interleave(th.arange(len(etypes), device=device),
                                              th.tensor(etypes, device=device))
            weight = weight.view(-1, weight.shape[2])
            flatidx = etypes * weight.shape[1] + h
            msg = weight.index_select(0, flatidx)
        elif self.low_mem:
            # A more memory-friendly implementation.
            # Calculate msg @ W_r before put msg into edge.
            assert isinstance(etypes, list)
            h_t = th.split(h, etypes)
            msg = []
            for etype in range(self.num_rels):
                if h_t[etype].shape[0] == 0:
                    continue
                if etype in self.active_rels: # check if this etype is active
                    msg.append(th.zeros(h_t[etype].shape))
                else:
                    msg.append(th.matmul(h_t[etype], weight[etype]))
            msg = th.cat(msg)
        else:
            # Use batched matmult
            active_idx = th.nonzero(edges.data["mask"]).squeeze()
            msg = th.zeros(h.shape[0], self.out_feat, device=device)
            if isinstance(etypes, list):
                etypes = th.repeat_interleave(th.arange(len(etypes), device=device),
                                              th.tensor(etypes, device=device))
            weight = weight.index_select(0, etypes)
            msg[active_idx] = th.bmm(h.unsqueeze(1), weight).squeeze(1)[active_idx]

        if 'norm' in edges.data:
            msg = msg * edges.data['norm']
        if 'feat' in edges.data:
            edge_feat_seeds = th.nonzero(th.logical_and(edges.data["efeat_bool"], edges.data["mask"]).int()).squeeze()
            if edge_feat_seeds.shape[0] != 0:
                msg[edge_feat_seeds] = self.edge_feat_transform(msg[edge_feat_seeds],edges.data["feat"][edge_feat_seeds])
        return {'msg': msg}

    def bdd_message_func(self, edges, etypes):
        """Message function for block-diagonal-decomposition regularizer.

        Parameters
        ----------
        edges : dgl.EdgeBatch
            Input to DGL message UDF.
        etypes : torch.Tensor or list[int]
            Edge type data. Could be either:

                * An :math:`(|E|,)` dense tensor. Each element corresponds to the edge's type ID.
                  Preferred format if ``lowmem == False``.
                * An integer list. The i^th element is the number of edges of the i^th type.
                  This requires the input graph to store edges sorted by their type IDs.
                  Preferred format if ``lowmem == True``.
        """
        h = edges.src['h']
        device = h.device

        if h.dtype == th.int64 and h.ndim == 1:
            raise TypeError('Block decomposition does not allow integer ID feature.')

        if self.low_mem:
            # A more memory-friendly implementation.
            # Calculate msg @ W_r before put msg into edge.
            assert isinstance(etypes, list)
            h_t = th.split(h, etypes)
            msg = []
            for etype in range(self.num_rels):
                if h_t[etype].shape[0] == 0:
                    continue
                if etype in self.active_rels: # check if this etype is active
                    msg.append(th.zeros(h_t[etype].shape))
                else:
                    tmp_w = self.weight[etype].view(self.num_bases, self.submat_in, self.submat_out)
                    tmp_h = h_t[etype].view(-1, self.num_bases, self.submat_in)
                    msg.append(th.einsum('abc,bcd->abd', tmp_h, tmp_w).reshape(-1, self.out_feat))
            msg = th.cat(msg)
        else:
            # Use batched matmult
            active_idx = th.nonzero(edges.data["mask"]).squeeze()
            msg = th.zeros(h.shape[0], self.out_feat, device=device)
            if isinstance(etypes, list):
                etypes = th.repeat_interleave(th.arange(len(etypes), device=device),
                                              th.tensor(etypes, device=device))
            weight = self.weight.index_select(0, etypes).view(
                -1, self.submat_in, self.submat_out)
            node = h.view(-1, 1, self.submat_in)
            msg[active_idx] = th.bmm(node, weight).view(-1, self.out_feat)[active_idx]
        if 'norm' in edges.data:
            msg = msg * edges.data['norm']
        if 'feat' in edges.data:
            edge_feat_seeds = th.nonzero(th.logical_and(edges.data["efeat_bool"], edges.data["mask"]).int()).squeeze()
            if edge_feat_seeds.shape[0] != 0:
                msg[edge_feat_seeds] = self.edge_feat_transform(msg[edge_feat_seeds], edges.data["feat"][edge_feat_seeds])
        return {'msg': msg}

    def forward(self, g, feat, etypes, norm=None, edge_feat = None, efeat_bool=None):
        """Forward computation.

        Parameters
        ----------
        g : DGLGraph
            The graph.
        feat : torch.Tensor
            Input node features. Could be either

                * :math:`(|V|, D)` dense tensor
                * :math:`(|V|,)` int64 vector, representing the categorical values of each
                  node. It then treat the input feature as an one-hot encoding feature.
        etypes : torch.Tensor or list[int]
            Edge type data. Could be either

                * An :math:`(|E|,)` dense tensor. Each element corresponds to the edge's type ID.
                  Preferred format if ``lowmem == False``.
                * An integer list. The i^th element is the number of edges of the i^th type.
                  This requires the input graph to store edges sorted by their type IDs.
                  Preferred format if ``lowmem == True``.
        norm : torch.Tensor
            Optional edge normalizer tensor. Shape: :math:`(|E|, 1)`.
        edge_feat : torch.Tensor
            Optional argument for the edge features
        efeat_bool : torch.Tensor
            Optional argument to specify which edges in the batch are associated with features for the rest the layer
            behaves as an RGCN

        Returns
        -------
        torch.Tensor
            New node features.

        Notes
        -----
        Under the ``low_mem`` mode, DGL will sort the graph based on the edge types
        and compute message passing one type at a time. DGL recommends sorts the
        graph beforehand (and cache it if possible) and provides the integer list
        format to the ``etypes`` argument. Use DGL's :func:`~dgl.to_homogeneous` API
        to get a sorted homogeneous graph from a heterogeneous graph. Pass ``return_count=True``
        to it to get the ``etypes`` in integer list.
        """
        if isinstance(etypes, th.Tensor):
            if len(etypes) != g.num_edges():
                raise DGLError('"etypes" tensor must have length equal to the number of edges'
                               ' in the graph. But got {} and {}.'.format(
                                   len(etypes), g.num_edges()))
            if self.low_mem and not (feat.dtype == th.int64 and feat.ndim == 1):
                # Low-mem optimization is not enabled for node ID input. When enabled,
                # it first sorts the graph based on the edge types (the sorting will not
                # change the node IDs). It then converts the etypes tensor to an integer
                # list, where each element is the number of edges of the type.
                # Sort the graph based on the etypes
                sorted_etypes, index = th.sort(etypes)
                g = dgl.edge_subgraph(g, index, relabel_nodes=False)
                # Create a new etypes to be an integer list of number of edges.
                pos = th.searchsorted(sorted_etypes, th.arange(self.num_rels, device=g.device))
                num = th.tensor([len(etypes)], device=g.device)
                etypes = (th.cat([pos[1:], num]) - pos).tolist()
                if norm is not None:
                    norm = norm[index]

        with g.local_scope():
            g.srcdata['h'] = feat
            if norm is not None:
                g.edata['norm'] = norm
            if edge_feat is not None:
                g.edata['feat'] = edge_feat
                g.edata['efeat_bool'] = efeat_bool
            g.edata['mask'] = sum(etypes==i for i in self.active_rels)
            if self.self_loop:
                loop_message = matmul_maybe_select(feat[:g.number_of_dst_nodes()],
                                                   self.loop_weight)
            # message passing
            g.update_all(functools.partial(self.message_func, etypes=etypes),
                         fn.sum(msg='msg', out='h'))

            # apply bias and activation
            if 'h' in g.dstdata and len(g.dstdata['h'].shape) == 2:
                node_repr = g.dstdata['h']
            else:
                node_repr = th.zeros((g.number_of_dst_nodes(), self.out_feat),
                                     dtype=feat.dtype,
                                     device=feat.device)
            if self.layer_norm:
                node_repr = self.layer_norm_weight(node_repr)
            if self.bias:
                node_repr = node_repr + self.h_bias
            if self.self_loop:
                node_repr = node_repr + loop_message
            if self.activation:
                node_repr = self.activation(node_repr)
            node_repr = self.dropout(node_repr)
            return node_repr


class NodeTypeEmbedding(nn.Module):
    r"""

   Parameters
   ----------
   in_units : int
       Size of input features
   embed_dim: int
       Size of embedding dimension
    """

    def __init__(self, num_n_types, num_props=2, embed_dim=16, device='cuda'):
        super(NodeTypeEmbedding, self).__init__()

        self.embed_size = embed_dim
        self.num_n_types = num_n_types
        self.num_props = num_props
        self.device = device
        self.ntype_embed = nn.Embedding(self.num_n_types, self.embed_size).to(self.device)

    def forward(self, g, node_ids):
        graph = dgl.block_to_graph(g[0])
        node_tids = graph.ndata[dgl.NTYPE]
        node_types = graph.ntypes
        graph = dgl.add_reverse_edges(dgl.to_homogeneous(graph)).to(self.device)
        h = th.empty((graph.num_nodes(), self.embed_size)).to(self.device)
        for i, n in enumerate(node_types):
            h[graph.ndata[dgl.NTYPE] == i] = self.ntype_embed(node_tids[n].to(self.device))
        with graph.local_scope():
            for i in range(self.num_props):
                graph.ndata['h'] = h
                graph.update_all(fn.copy_src('h', 'm'), fn.sum('m', 'h_new'))
                h = graph.ndata['h_new']

        return h[graph.ndata[dgl.NTYPE] == 0]