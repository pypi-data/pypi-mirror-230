import json

MORPHO_AAVE_V3_COMPTROLLER_ABI = json.loads('''
[
  {
    "inputs": [],
    "name": "AddressIsZero",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "AmountIsZero",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "UnsafeCast",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "AssetIsCollateralOnMorpho",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "AssetNotCollateralOnMorpho",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "AssetNotCollateralOnPool",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "BorrowIsPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "BorrowNotEnabled",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "BorrowNotPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ClaimRewardsPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "CollateralIsZero",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "DebtIsZero",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ExceedsBorrowCap",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ExceedsMaxBasisPoints",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InconsistentEMode",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InvalidNonce",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InvalidSignatory",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InvalidValueS",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "InvalidValueV",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "LiquidateBorrowIsPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "LiquidateCollateralIsPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MarketAlreadyCreated",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MarketIsDeprecated",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MarketIsNotListedOnAave",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MarketLtTooLow",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MarketNotCreated",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "PermissionDenied",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "RepayIsPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SentinelBorrowNotEnabled",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SentinelLiquidateNotEnabled",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SetAsCollateralOnPoolButMarketNotCreated",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SignatureExpired",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SiloedBorrowMarket",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SupplyCollateralIsPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SupplyIsPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SupplyIsZero",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "UnauthorizedBorrow",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "UnauthorizedLiquidate",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "UnauthorizedWithdraw",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "WithdrawCollateralIsPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "WithdrawIsPaused",
    "type": "error"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "uint8",
        "name": "version",
        "type": "uint8"
      }
    ],
    "name": "Initialized",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "OwnershipTransferStarted",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "OwnershipTransferred",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "user",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledInP2P",
        "type": "uint256"
      }
    ],
    "name": "BorrowPositionUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "address",
        "name": "caller",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledInP2P",
        "type": "uint256"
      }
    ],
    "name": "Borrowed",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledBalance",
        "type": "uint256"
      }
    ],
    "name": "CollateralSupplied",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "address",
        "name": "caller",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledBalance",
        "type": "uint256"
      }
    ],
    "name": "CollateralWithdrawn",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "uint128",
        "name": "repay",
        "type": "uint128"
      },
      {
        "indexed": false,
        "internalType": "uint128",
        "name": "withdraw",
        "type": "uint128"
      }
    ],
    "name": "DefaultIterationsSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "idleSupply",
        "type": "uint256"
      }
    ],
    "name": "IdleSupplyUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "poolSupplyIndex",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "p2pSupplyIndex",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "poolBorrowIndex",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "p2pBorrowIndex",
        "type": "uint256"
      }
    ],
    "name": "IndexesUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "IsBorrowPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "IsClaimRewardsPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isCollateral",
        "type": "bool"
      }
    ],
    "name": "IsCollateralSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isDeprecated",
        "type": "bool"
      }
    ],
    "name": "IsDeprecatedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "IsLiquidateBorrowPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "IsLiquidateCollateralPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isP2PDisabled",
        "type": "bool"
      }
    ],
    "name": "IsP2PDisabledSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "IsRepayPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "IsSupplyCollateralPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "IsSupplyPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "IsWithdrawCollateralPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "IsWithdrawPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "liquidator",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "borrower",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlyingBorrowed",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amountLiquidated",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "address",
        "name": "underlyingCollateral",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amountSeized",
        "type": "uint256"
      }
    ],
    "name": "Liquidated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "delegator",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "manager",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isAllowed",
        "type": "bool"
      }
    ],
    "name": "ManagerApproval",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      }
    ],
    "name": "MarketCreated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledDelta",
        "type": "uint256"
      }
    ],
    "name": "P2PBorrowDeltaUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "P2PDeltasIncreased",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "p2pIndexCursor",
        "type": "uint16"
      }
    ],
    "name": "P2PIndexCursorSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledDelta",
        "type": "uint256"
      }
    ],
    "name": "P2PSupplyDeltaUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledTotalSupplyP2P",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledTotalBorrowP2P",
        "type": "uint256"
      }
    ],
    "name": "P2PTotalsUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "positionsManager",
        "type": "address"
      }
    ],
    "name": "PositionsManagerSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "repayer",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledInP2P",
        "type": "uint256"
      }
    ],
    "name": "Repaid",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "reserveFactor",
        "type": "uint16"
      }
    ],
    "name": "ReserveFactorSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "claimed",
        "type": "uint256"
      }
    ],
    "name": "ReserveFeeClaimed",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "claimer",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "rewardToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amountClaimed",
        "type": "uint256"
      }
    ],
    "name": "RewardsClaimed",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "rewardsManager",
        "type": "address"
      }
    ],
    "name": "RewardsManagerSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledInP2P",
        "type": "uint256"
      }
    ],
    "name": "Supplied",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "user",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledInP2P",
        "type": "uint256"
      }
    ],
    "name": "SupplyPositionUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "treasuryVault",
        "type": "address"
      }
    ],
    "name": "TreasuryVaultSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "caller",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "signatory",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "usedNonce",
        "type": "uint256"
      }
    ],
    "name": "UserNonceIncremented",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "address",
        "name": "caller",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "scaledInP2P",
        "type": "uint256"
      }
    ],
    "name": "Withdrawn",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "DOMAIN_SEPARATOR",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "acceptOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "addressesProvider",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "manager",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isAllowed",
        "type": "bool"
      }
    ],
    "name": "approveManager",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "delegator",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "manager",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isAllowed",
        "type": "bool"
      },
      {
        "internalType": "uint256",
        "name": "nonce",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      },
      {
        "components": [
          {
            "internalType": "uint8",
            "name": "v",
            "type": "uint8"
          },
          {
            "internalType": "bytes32",
            "name": "r",
            "type": "bytes32"
          },
          {
            "internalType": "bytes32",
            "name": "s",
            "type": "bytes32"
          }
        ],
        "internalType": "struct Types.Signature",
        "name": "signature",
        "type": "tuple"
      }
    ],
    "name": "approveManagerWithSig",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "maxIterations",
        "type": "uint256"
      }
    ],
    "name": "borrow",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "borrowBalance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address[]",
        "name": "assets",
        "type": "address[]"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      }
    ],
    "name": "claimRewards",
    "outputs": [
      {
        "internalType": "address[]",
        "name": "rewardTokens",
        "type": "address[]"
      },
      {
        "internalType": "uint256[]",
        "name": "claimedAmounts",
        "type": "uint256[]"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address[]",
        "name": "underlyings",
        "type": "address[]"
      },
      {
        "internalType": "uint256[]",
        "name": "amounts",
        "type": "uint256[]"
      }
    ],
    "name": "claimToTreasury",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "collateralBalance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint16",
        "name": "reserveFactor",
        "type": "uint16"
      },
      {
        "internalType": "uint16",
        "name": "p2pIndexCursor",
        "type": "uint16"
      }
    ],
    "name": "createMarket",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "defaultIterations",
    "outputs": [
      {
        "components": [
          {
            "internalType": "uint128",
            "name": "repay",
            "type": "uint128"
          },
          {
            "internalType": "uint128",
            "name": "withdraw",
            "type": "uint128"
          }
        ],
        "internalType": "struct Types.Iterations",
        "name": "",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "eModeCategoryId",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "enum Types.Position",
        "name": "position",
        "type": "uint8"
      }
    ],
    "name": "getBucketsMask",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "enum Types.Position",
        "name": "position",
        "type": "uint8"
      },
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "getNext",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "increaseP2PDeltas",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "addressesProvider",
        "type": "address"
      },
      {
        "internalType": "uint8",
        "name": "eModeCategoryId",
        "type": "uint8"
      },
      {
        "internalType": "address",
        "name": "positionsManager",
        "type": "address"
      },
      {
        "components": [
          {
            "internalType": "uint128",
            "name": "repay",
            "type": "uint128"
          },
          {
            "internalType": "uint128",
            "name": "withdraw",
            "type": "uint128"
          }
        ],
        "internalType": "struct Types.Iterations",
        "name": "defaultIterations",
        "type": "tuple"
      }
    ],
    "name": "initialize",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isClaimRewardsPaused",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "delegator",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "manager",
        "type": "address"
      }
    ],
    "name": "isManagedBy",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlyingBorrowed",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "underlyingCollateral",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "liquidate",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "liquidityData",
    "outputs": [
      {
        "components": [
          {
            "internalType": "uint256",
            "name": "borrowable",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "maxDebt",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "debt",
            "type": "uint256"
          }
        ],
        "internalType": "struct Types.LiquidityData",
        "name": "",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      }
    ],
    "name": "market",
    "outputs": [
      {
        "components": [
          {
            "components": [
              {
                "components": [
                  {
                    "internalType": "uint128",
                    "name": "poolIndex",
                    "type": "uint128"
                  },
                  {
                    "internalType": "uint128",
                    "name": "p2pIndex",
                    "type": "uint128"
                  }
                ],
                "internalType": "struct Types.MarketSideIndexes",
                "name": "supply",
                "type": "tuple"
              },
              {
                "components": [
                  {
                    "internalType": "uint128",
                    "name": "poolIndex",
                    "type": "uint128"
                  },
                  {
                    "internalType": "uint128",
                    "name": "p2pIndex",
                    "type": "uint128"
                  }
                ],
                "internalType": "struct Types.MarketSideIndexes",
                "name": "borrow",
                "type": "tuple"
              }
            ],
            "internalType": "struct Types.Indexes",
            "name": "indexes",
            "type": "tuple"
          },
          {
            "components": [
              {
                "components": [
                  {
                    "internalType": "uint256",
                    "name": "scaledDelta",
                    "type": "uint256"
                  },
                  {
                    "internalType": "uint256",
                    "name": "scaledP2PTotal",
                    "type": "uint256"
                  }
                ],
                "internalType": "struct Types.MarketSideDelta",
                "name": "supply",
                "type": "tuple"
              },
              {
                "components": [
                  {
                    "internalType": "uint256",
                    "name": "scaledDelta",
                    "type": "uint256"
                  },
                  {
                    "internalType": "uint256",
                    "name": "scaledP2PTotal",
                    "type": "uint256"
                  }
                ],
                "internalType": "struct Types.MarketSideDelta",
                "name": "borrow",
                "type": "tuple"
              }
            ],
            "internalType": "struct Types.Deltas",
            "name": "deltas",
            "type": "tuple"
          },
          {
            "internalType": "address",
            "name": "underlying",
            "type": "address"
          },
          {
            "components": [
              {
                "internalType": "bool",
                "name": "isP2PDisabled",
                "type": "bool"
              },
              {
                "internalType": "bool",
                "name": "isSupplyPaused",
                "type": "bool"
              },
              {
                "internalType": "bool",
                "name": "isSupplyCollateralPaused",
                "type": "bool"
              },
              {
                "internalType": "bool",
                "name": "isBorrowPaused",
                "type": "bool"
              },
              {
                "internalType": "bool",
                "name": "isWithdrawPaused",
                "type": "bool"
              },
              {
                "internalType": "bool",
                "name": "isWithdrawCollateralPaused",
                "type": "bool"
              },
              {
                "internalType": "bool",
                "name": "isRepayPaused",
                "type": "bool"
              },
              {
                "internalType": "bool",
                "name": "isLiquidateCollateralPaused",
                "type": "bool"
              },
              {
                "internalType": "bool",
                "name": "isLiquidateBorrowPaused",
                "type": "bool"
              },
              {
                "internalType": "bool",
                "name": "isDeprecated",
                "type": "bool"
              }
            ],
            "internalType": "struct Types.PauseStatuses",
            "name": "pauseStatuses",
            "type": "tuple"
          },
          {
            "internalType": "bool",
            "name": "isCollateral",
            "type": "bool"
          },
          {
            "internalType": "address",
            "name": "variableDebtToken",
            "type": "address"
          },
          {
            "internalType": "uint32",
            "name": "lastUpdateTimestamp",
            "type": "uint32"
          },
          {
            "internalType": "uint16",
            "name": "reserveFactor",
            "type": "uint16"
          },
          {
            "internalType": "uint16",
            "name": "p2pIndexCursor",
            "type": "uint16"
          },
          {
            "internalType": "address",
            "name": "aToken",
            "type": "address"
          },
          {
            "internalType": "address",
            "name": "stableDebtToken",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "idleSupply",
            "type": "uint256"
          }
        ],
        "internalType": "struct Types.Market",
        "name": "",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "marketsCreated",
    "outputs": [
      {
        "internalType": "address[]",
        "name": "",
        "type": "address[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "pendingOwner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "pool",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "positionsManager",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      }
    ],
    "name": "repay",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      },
      {
        "components": [
          {
            "internalType": "uint8",
            "name": "v",
            "type": "uint8"
          },
          {
            "internalType": "bytes32",
            "name": "r",
            "type": "bytes32"
          },
          {
            "internalType": "bytes32",
            "name": "s",
            "type": "bytes32"
          }
        ],
        "internalType": "struct Types.Signature",
        "name": "signature",
        "type": "tuple"
      }
    ],
    "name": "repayWithPermit",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "rewardsManager",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "scaledCollateralBalance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "scaledP2PBorrowBalance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "scaledP2PSupplyBalance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "scaledPoolBorrowBalance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "scaledPoolSupplyBalance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isCollateral",
        "type": "bool"
      }
    ],
    "name": "setAssetIsCollateral",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isCollateral",
        "type": "bool"
      }
    ],
    "name": "setAssetIsCollateralOnPool",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "components": [
          {
            "internalType": "uint128",
            "name": "repay",
            "type": "uint128"
          },
          {
            "internalType": "uint128",
            "name": "withdraw",
            "type": "uint128"
          }
        ],
        "internalType": "struct Types.Iterations",
        "name": "defaultIterations",
        "type": "tuple"
      }
    ],
    "name": "setDefaultIterations",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsBorrowPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsClaimRewardsPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isDeprecated",
        "type": "bool"
      }
    ],
    "name": "setIsDeprecated",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsLiquidateBorrowPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsLiquidateCollateralPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isP2PDisabled",
        "type": "bool"
      }
    ],
    "name": "setIsP2PDisabled",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsPausedForAllMarkets",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsRepayPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsSupplyCollateralPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsSupplyPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsWithdrawCollateralPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsWithdrawPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint16",
        "name": "p2pIndexCursor",
        "type": "uint16"
      }
    ],
    "name": "setP2PIndexCursor",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "positionsManager",
        "type": "address"
      }
    ],
    "name": "setPositionsManager",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint16",
        "name": "newReserveFactor",
        "type": "uint16"
      }
    ],
    "name": "setReserveFactor",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "rewardsManager",
        "type": "address"
      }
    ],
    "name": "setRewardsManager",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "treasuryVault",
        "type": "address"
      }
    ],
    "name": "setTreasuryVault",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "maxIterations",
        "type": "uint256"
      }
    ],
    "name": "supply",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "supplyBalance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      }
    ],
    "name": "supplyCollateral",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      },
      {
        "components": [
          {
            "internalType": "uint8",
            "name": "v",
            "type": "uint8"
          },
          {
            "internalType": "bytes32",
            "name": "r",
            "type": "bytes32"
          },
          {
            "internalType": "bytes32",
            "name": "s",
            "type": "bytes32"
          }
        ],
        "internalType": "struct Types.Signature",
        "name": "signature",
        "type": "tuple"
      }
    ],
    "name": "supplyCollateralWithPermit",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "maxIterations",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      },
      {
        "components": [
          {
            "internalType": "uint8",
            "name": "v",
            "type": "uint8"
          },
          {
            "internalType": "bytes32",
            "name": "r",
            "type": "bytes32"
          },
          {
            "internalType": "bytes32",
            "name": "s",
            "type": "bytes32"
          }
        ],
        "internalType": "struct Types.Signature",
        "name": "signature",
        "type": "tuple"
      }
    ],
    "name": "supplyWithPermit",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "transferOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "treasuryVault",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      }
    ],
    "name": "updatedIndexes",
    "outputs": [
      {
        "components": [
          {
            "components": [
              {
                "internalType": "uint256",
                "name": "poolIndex",
                "type": "uint256"
              },
              {
                "internalType": "uint256",
                "name": "p2pIndex",
                "type": "uint256"
              }
            ],
            "internalType": "struct Types.MarketSideIndexes256",
            "name": "supply",
            "type": "tuple"
          },
          {
            "components": [
              {
                "internalType": "uint256",
                "name": "poolIndex",
                "type": "uint256"
              },
              {
                "internalType": "uint256",
                "name": "p2pIndex",
                "type": "uint256"
              }
            ],
            "internalType": "struct Types.MarketSideIndexes256",
            "name": "borrow",
            "type": "tuple"
          }
        ],
        "internalType": "struct Types.Indexes256",
        "name": "indexes",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "userBorrows",
    "outputs": [
      {
        "internalType": "address[]",
        "name": "",
        "type": "address[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "userCollaterals",
    "outputs": [
      {
        "internalType": "address[]",
        "name": "",
        "type": "address[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "userNonce",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "maxIterations",
        "type": "uint256"
      }
    ],
    "name": "withdraw",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "underlying",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      }
    ],
    "name": "withdrawCollateral",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
''')